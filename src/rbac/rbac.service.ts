import {
  ConflictException,
  Injectable,
  NotFoundException,
} from '@nestjs/common';
import { AuthService } from '../auth/auth.service';
import { PrismaService } from '../prisma/prisma.service';
import { AssignPermissionToUserDto } from './dto/assign-permission.dto';
import {
  CreateIdentificationTypeDto,
  UpdateIdentificationTypeDto,
} from './dto/create-identification-type.dto';
import {
  CreatePermissionDto,
  UpdatePermissionDto,
} from './dto/create-permission.dto';
import { CreateRoleDto, UpdateRoleDto } from './dto/create-role.dto';

@Injectable()
export class RbacService {
  constructor(
    private readonly prisma: PrismaService,
    private readonly authService: AuthService,
  ) {}

  // --- Tipos de identificación ---

  createIdentificationType(dto: CreateIdentificationTypeDto) {
    return this.prisma.identificationType.create({
      data: { code: dto.code.toUpperCase(), name: dto.name },
    });
  }

  findAllIdentificationTypes() {
    return this.prisma.identificationType.findMany({
      orderBy: { code: 'asc' },
    });
  }

  async findIdentificationTypeById(id: string) {
    const row = await this.prisma.identificationType.findUnique({
      where: { id },
    });
    if (!row)
      throw new NotFoundException('Tipo de identificación no encontrado');
    return row;
  }

  async updateIdentificationType(id: string, dto: UpdateIdentificationTypeDto) {
    await this.findIdentificationTypeById(id);
    return this.prisma.identificationType.update({
      where: { id },
      data: {
        ...(dto.code !== undefined && { code: dto.code.toUpperCase() }),
        ...(dto.name !== undefined && { name: dto.name }),
      },
    });
  }

  // --- Proveedores OAuth (catálogo) ---

  findAllAuthProviders() {
    return this.prisma.authProvider.findMany({ orderBy: { code: 'asc' } });
  }

  // --- Roles ---

  async createRole(dto: CreateRoleDto) {
    try {
      return await this.prisma.role.create({
        data: {
          code: dto.code.toUpperCase(),
          name: dto.name,
          description: dto.description ?? null,
        },
      });
    } catch {
      throw new ConflictException('Código de rol duplicado');
    }
  }

  findAllRoles() {
    return this.prisma.role.findMany({
      orderBy: { code: 'asc' },
      include: {
        rolePermissions: { include: { permission: true } },
      },
    });
  }

  async findRoleById(id: string) {
    const row = await this.prisma.role.findUnique({
      where: { id },
      include: {
        rolePermissions: { include: { permission: true } },
      },
    });
    if (!row) throw new NotFoundException('Rol no encontrado');
    return row;
  }

  async updateRole(id: string, dto: UpdateRoleDto) {
    await this.findRoleById(id);
    try {
      return await this.prisma.role.update({
        where: { id },
        data: {
          ...(dto.code !== undefined && { code: dto.code.toUpperCase() }),
          ...(dto.name !== undefined && { name: dto.name }),
          ...(dto.description !== undefined && {
            description: dto.description,
          }),
        },
      });
    } catch {
      throw new ConflictException('Código de rol duplicado');
    }
  }

  async addPermissionToRole(roleId: string, permissionId: string) {
    await this.findRoleById(roleId);
    const perm = await this.prisma.permission.findUnique({
      where: { id: permissionId },
    });
    if (!perm) throw new NotFoundException('Permiso no encontrado');
    return this.prisma.rolePermission.create({
      data: { roleId, permissionId },
      include: { permission: true, role: true },
    });
  }

  async removePermissionFromRole(roleId: string, permissionId: string) {
    try {
      await this.prisma.rolePermission.delete({
        where: {
          roleId_permissionId: { roleId, permissionId },
        },
      });
    } catch {
      throw new NotFoundException('Asignación rol-permiso no encontrada');
    }
    return { ok: true };
  }

  // --- Permisos (catálogo) ---

  async createPermission(dto: CreatePermissionDto) {
    try {
      return await this.prisma.permission.create({
        data: {
          code: dto.code,
          name: dto.name,
          description: dto.description ?? null,
        },
      });
    } catch {
      throw new ConflictException('Código de permiso duplicado');
    }
  }

  findAllPermissions() {
    return this.prisma.permission.findMany({ orderBy: { code: 'asc' } });
  }

  async findPermissionById(id: string) {
    const row = await this.prisma.permission.findUnique({ where: { id } });
    if (!row) throw new NotFoundException('Permiso no encontrado');
    return row;
  }

  async updatePermission(id: string, dto: UpdatePermissionDto) {
    await this.findPermissionById(id);
    try {
      return await this.prisma.permission.update({
        where: { id },
        data: {
          ...(dto.code !== undefined && { code: dto.code }),
          ...(dto.name !== undefined && { name: dto.name }),
          ...(dto.description !== undefined && {
            description: dto.description,
          }),
        },
      });
    } catch {
      throw new ConflictException('Código de permiso duplicado');
    }
  }

  // --- Usuario ↔ roles (auth_user_role) ---

  async addRoleToUser(userId: string, roleId: string) {
    const user = await this.prisma.user.findUnique({ where: { id: userId } });
    if (!user) throw new NotFoundException('Usuario no encontrado');
    await this.findRoleById(roleId);
    return this.prisma.userRole.create({
      data: { userId, roleId },
      include: { role: true },
    });
  }

  async removeRoleFromUser(userId: string, roleId: string) {
    try {
      await this.prisma.userRole.delete({
        where: { userId_roleId: { userId, roleId } },
      });
    } catch {
      throw new NotFoundException('Asignación usuario-rol no encontrada');
    }
    return { ok: true };
  }

  // --- Usuario ↔ permisos directos (auth_user_permission) ---

  async addOrUpdateUserPermission(
    userId: string,
    dto: AssignPermissionToUserDto,
  ) {
    const user = await this.prisma.user.findUnique({ where: { id: userId } });
    if (!user) throw new NotFoundException('Usuario no encontrado');
    await this.findPermissionById(dto.permissionId);
    const granted = dto.granted ?? true;
    return this.prisma.userPermission.upsert({
      where: {
        userId_permissionId: {
          userId,
          permissionId: dto.permissionId,
        },
      },
      create: {
        userId,
        permissionId: dto.permissionId,
        granted,
      },
      update: { granted },
      include: { permission: true },
    });
  }

  async removeUserPermission(userId: string, permissionId: string) {
    try {
      await this.prisma.userPermission.delete({
        where: {
          userId_permissionId: { userId, permissionId },
        },
      });
    } catch {
      throw new NotFoundException('Asignación usuario-permiso no encontrada');
    }
    return { ok: true };
  }

  async effectivePermissionsForUser(userId: string) {
    const user = await this.prisma.user.findUnique({ where: { id: userId } });
    if (!user) throw new NotFoundException('Usuario no encontrado');
    const codes = await this.authService.getEffectivePermissionCodes(userId);
    return { userId, permissionCodes: codes };
  }
}
