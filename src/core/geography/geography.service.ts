import {
  BadRequestException,
  Injectable,
  NotFoundException,
} from '@nestjs/common';
import { Prisma } from '@prisma/client';
import { PrismaService } from '../../prisma/prisma.service';
import { CreateAdministrativeDivisionDto } from './dto/create-administrative-division.dto';
import { CreateCountryDto } from './dto/create-country.dto';
import { CreateDivisionTypeDto } from './dto/create-division-type.dto';
import { UpdateAdministrativeDivisionDto } from './dto/update-administrative-division.dto';

@Injectable()
export class GeographyService {
  constructor(private readonly prisma: PrismaService) {}

  createCountry(dto: CreateCountryDto) {
    return this.prisma.country.create({ data: dto });
  }

  findAllCountries() {
    return this.prisma.country.findMany({ orderBy: { name: 'asc' } });
  }

  async findCountryById(id: string) {
    const row = await this.prisma.country.findUnique({ where: { id } });
    if (!row) throw new NotFoundException('País no encontrado');
    return row;
  }

  createDivisionType(dto: CreateDivisionTypeDto) {
    return this.prisma.divisionType.create({
      data: {
        name: dto.name,
        level: dto.level,
        countryId: dto.countryId ?? null,
      },
    });
  }

  findAllDivisionTypes() {
    return this.prisma.divisionType.findMany({
      orderBy: [{ level: 'asc' }, { name: 'asc' }],
    });
  }

  async findDivisionTypeById(id: string) {
    const row = await this.prisma.divisionType.findUnique({ where: { id } });
    if (!row) throw new NotFoundException('Tipo de división no encontrado');
    return row;
  }

  async createAdministrativeDivision(dto: CreateAdministrativeDivisionDto) {
    const parentId = dto.parentId ?? null;
    await this.assertAdministrativeDivisionRules(
      {
        name: dto.name,
        countryId: dto.countryId,
        parentId,
        divisionTypeId: dto.divisionTypeId,
      },
      undefined,
    );

    return this.prisma.administrativeDivision.create({
      data: {
        name: dto.name,
        code: dto.code ?? null,
        countryId: dto.countryId,
        parentId,
        divisionTypeId: dto.divisionTypeId,
      },
    });
  }

  findAllAdministrativeDivisions() {
    return this.prisma.administrativeDivision.findMany({
      orderBy: [{ countryId: 'asc' }, { name: 'asc' }],
      include: { divisionType: true, parent: true },
    });
  }

  async findAdministrativeDivisionById(id: string) {
    const row = await this.prisma.administrativeDivision.findUnique({
      where: { id },
      include: { divisionType: true, parent: true, children: true },
    });
    if (!row) {
      throw new NotFoundException('División administrativa no encontrada');
    }
    return row;
  }

  async updateAdministrativeDivision(
    id: string,
    dto: UpdateAdministrativeDivisionDto,
  ) {
    const existing = await this.prisma.administrativeDivision.findUnique({
      where: { id },
    });
    if (!existing) {
      throw new NotFoundException('División administrativa no encontrada');
    }

    const parentId =
      dto.parentId !== undefined ? dto.parentId : existing.parentId;

    if (dto.parentId !== undefined && dto.parentId === id) {
      throw new BadRequestException(
        'Una división no puede ser padre de sí misma',
      );
    }

    const next = {
      name: dto.name ?? existing.name,
      countryId: dto.countryId ?? existing.countryId,
      parentId,
      divisionTypeId: dto.divisionTypeId ?? existing.divisionTypeId,
    };

    await this.assertAdministrativeDivisionRules(next, id);

    const data: Prisma.AdministrativeDivisionUpdateInput = {};
    if (dto.name !== undefined) data.name = dto.name;
    if (dto.code !== undefined) data.code = dto.code;
    if (dto.countryId !== undefined) {
      data.country = { connect: { id: dto.countryId } };
    }
    if (dto.parentId !== undefined) {
      data.parent = dto.parentId
        ? { connect: { id: dto.parentId } }
        : { disconnect: true };
    }
    if (dto.divisionTypeId !== undefined) {
      data.divisionType = { connect: { id: dto.divisionTypeId } };
    }

    return this.prisma.administrativeDivision.update({
      where: { id },
      data,
      include: { divisionType: true, parent: true },
    });
  }

  private async assertAdministrativeDivisionRules(
    params: {
      name: string;
      countryId: string;
      parentId: string | null;
      divisionTypeId: string;
    },
    excludeDivisionId?: string,
  ): Promise<void> {
    const divisionType = await this.prisma.divisionType.findUnique({
      where: { id: params.divisionTypeId },
    });
    if (!divisionType) {
      throw new BadRequestException('Tipo de división no encontrado');
    }

    if (params.parentId) {
      const parent = await this.prisma.administrativeDivision.findUnique({
        where: { id: params.parentId },
        include: { divisionType: true },
      });
      if (!parent) {
        throw new BadRequestException('División padre no encontrada');
      }
      if (parent.countryId !== params.countryId) {
        throw new BadRequestException('El padre debe pertenecer al mismo país');
      }
      if (parent.divisionType.level >= divisionType.level) {
        throw new BadRequestException(
          'La jerarquía es inválida: el padre debe ser de nivel menor',
        );
      }
    } else {
      if (divisionType.level !== 1) {
        throw new BadRequestException(
          'Solo divisiones de nivel 1 pueden no tener padre',
        );
      }
      const dupRoot = await this.prisma.administrativeDivision.findFirst({
        where: {
          countryId: params.countryId,
          parentId: null,
          name: params.name,
          ...(excludeDivisionId ? { id: { not: excludeDivisionId } } : {}),
        },
      });
      if (dupRoot) {
        throw new BadRequestException(
          'Ya existe una división raíz con este nombre en el país',
        );
      }
    }
  }
}
