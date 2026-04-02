import {
  ConflictException,
  Injectable,
  UnauthorizedException,
} from '@nestjs/common';
import { JwtService } from '@nestjs/jwt';
import { User } from '@prisma/client';
import * as bcrypt from 'bcrypt';
import { PrismaService } from '../prisma/prisma.service';
import { RegisterDto } from './dto/register.dto';

const BCRYPT_ROUNDS = 10;

export type SafeUser = Omit<User, 'passwordHash'>;

@Injectable()
export class AuthService {
  constructor(
    private readonly prisma: PrismaService,
    private readonly jwtService: JwtService,
  ) {}

  async register(dto: RegisterDto) {
    const existing = await this.prisma.user.findUnique({
      where: { email: dto.email.toLowerCase() },
    });
    if (existing) {
      throw new ConflictException('El correo ya está registrado');
    }

    const passwordHash = await bcrypt.hash(dto.password, BCRYPT_ROUNDS);
    const email = dto.email.toLowerCase();

    const user = await this.prisma.$transaction(async (tx) => {
      const person = await tx.person.create({
        data: {
          firstName: dto.firstName,
          lastName: dto.lastName,
          emailPersonal: email,
          identification: dto.identification ?? null,
          identificationTypeId: dto.identificationTypeId ?? null,
          countryId: dto.countryId ?? null,
          phone: dto.phone ?? null,
        },
      });

      return tx.user.create({
        data: {
          email,
          passwordHash,
          personId: person.id,
        },
        include: { person: true },
      });
    });

    return this.buildAuthResponse(user);
  }

  async validateUser(
    email: string,
    password: string,
  ): Promise<SafeUser | null> {
    const user = await this.prisma.user.findUnique({
      where: { email: email.toLowerCase() },
    });
    if (!user || !user.passwordHash || !user.isActive) {
      return null;
    }
    const ok = await bcrypt.compare(password, user.passwordHash);
    if (!ok) return null;
    const { passwordHash, ...safe } = user;
    void passwordHash;
    return safe;
  }

  async issueTokensForUserId(userId: string) {
    const full = await this.prisma.user.findUnique({
      where: { id: userId },
      include: { person: true },
    });
    if (!full || !full.isActive) {
      throw new UnauthorizedException('Usuario no disponible');
    }
    return this.buildAuthResponse(full);
  }

  async findOrCreateOAuthUser(params: {
    providerCode: string;
    externalUserId: string;
    email: string;
    firstName?: string;
    lastName?: string;
  }) {
    const provider = await this.prisma.authProvider.findUnique({
      where: { code: params.providerCode },
    });
    if (!provider) {
      throw new UnauthorizedException('Proveedor OAuth no configurado');
    }

    const email = params.email.toLowerCase();
    const linked = await this.prisma.userAuthAccount.findFirst({
      where: {
        authProviderId: provider.id,
        externalUserId: params.externalUserId,
      },
      include: {
        user: {
          include: { person: true },
        },
      },
    });
    if (linked?.user.isActive && linked.user.person) {
      return this.buildAuthResponse(linked.user);
    }

    const existingByEmail = await this.prisma.user.findUnique({
      where: { email },
      include: { person: true },
    });

    if (existingByEmail?.isActive) {
      await this.prisma.userAuthAccount.upsert({
        where: {
          authProviderId_externalUserId: {
            authProviderId: provider.id,
            externalUserId: params.externalUserId,
          },
        },
        create: {
          userId: existingByEmail.id,
          authProviderId: provider.id,
          externalUserId: params.externalUserId,
          emailAtLink: email,
        },
        update: { emailAtLink: email },
      });
      const withPerson = await this.prisma.user.findUniqueOrThrow({
        where: { id: existingByEmail.id },
        include: { person: true },
      });
      return this.buildAuthResponse(withPerson);
    }

    const firstName =
      params.firstName?.trim() || email.split('@')[0] || 'Usuario';
    const lastName = params.lastName?.trim() || 'OAuth';

    const created = await this.prisma.$transaction(async (tx) => {
      const person = await tx.person.create({
        data: {
          firstName,
          lastName,
          emailPersonal: email,
        },
      });
      const user = await tx.user.create({
        data: {
          email,
          passwordHash: null,
          personId: person.id,
          emailVerified: true,
        },
        include: { person: true },
      });
      await tx.userAuthAccount.create({
        data: {
          userId: user.id,
          authProviderId: provider.id,
          externalUserId: params.externalUserId,
          emailAtLink: email,
        },
      });
      return user;
    });

    return this.buildAuthResponse(created);
  }

  async getProfile(userId: string) {
    const user = await this.prisma.user.findUnique({
      where: { id: userId },
      include: {
        person: {
          include: {
            country: true,
            identificationType: true,
            administrativeDivision: true,
            cityDivision: true,
          },
        },
        userRoles: { include: { role: true } },
        authAccounts: { include: { authProvider: true } },
      },
    });
    if (!user) {
      throw new UnauthorizedException();
    }
    const permissionCodes = await this.getEffectivePermissionCodes(userId);
    const { passwordHash, ...safe } = user;
    void passwordHash;
    return { ...safe, permissionCodes };
  }

  async getEffectivePermissionCodes(userId: string): Promise<string[]> {
    const user = await this.prisma.user.findUnique({
      where: { id: userId },
      include: {
        userRoles: {
          include: {
            role: {
              include: {
                rolePermissions: { include: { permission: true } },
              },
            },
          },
        },
        userPermissions: { include: { permission: true } },
      },
    });
    if (!user) return [];

    const fromRoles = new Set<string>();
    for (const ur of user.userRoles) {
      for (const rp of ur.role.rolePermissions) {
        fromRoles.add(rp.permission.code);
      }
    }

    const denied = new Set<string>();
    const extraGranted = new Set<string>();
    for (const up of user.userPermissions) {
      if (up.granted) extraGranted.add(up.permission.code);
      else denied.add(up.permission.code);
    }

    const merged = new Set<string>();
    for (const c of fromRoles) {
      if (!denied.has(c)) merged.add(c);
    }
    for (const c of extraGranted) {
      if (!denied.has(c)) merged.add(c);
    }
    return [...merged];
  }

  private async buildAuthResponse(
    user: User & { person: { firstName: string; lastName: string } },
  ) {
    const permissions = await this.getEffectivePermissionCodes(user.id);
    const payload = {
      sub: user.id,
      email: user.email,
      permissions,
    };
    const access_token = await this.jwtService.signAsync(payload);
    const { passwordHash, ...safe } = user;
    void passwordHash;
    return {
      access_token,
      user: safe,
      permissions,
    };
  }
}
