import { Body, Controller, Get, Param, Patch, Post } from '@nestjs/common';
import { ApiOperation, ApiParam, ApiTags } from '@nestjs/swagger';
import { CreateAdministrativeDivisionDto } from './dto/create-administrative-division.dto';
import { CreateCountryDto } from './dto/create-country.dto';
import { CreateDivisionTypeDto } from './dto/create-division-type.dto';
import { UpdateAdministrativeDivisionDto } from './dto/update-administrative-division.dto';
import { GeographyService } from './geography.service';

@ApiTags('geography')
@Controller('geography')
export class GeographyController {
  constructor(private readonly geographyService: GeographyService) {}

  @Post('countries')
  @ApiOperation({ summary: 'Crear país' })
  createCountry(@Body() dto: CreateCountryDto) {
    return this.geographyService.createCountry(dto);
  }

  @Get('countries')
  @ApiOperation({ summary: 'Listar países' })
  findAllCountries() {
    return this.geographyService.findAllCountries();
  }

  @Get('countries/:id')
  @ApiOperation({ summary: 'Obtener país por id' })
  @ApiParam({ name: 'id', description: 'ID del país (cuid)' })
  findCountryById(@Param('id') id: string) {
    return this.geographyService.findCountryById(id);
  }

  @Post('division-types')
  @ApiOperation({ summary: 'Crear tipo de división' })
  createDivisionType(@Body() dto: CreateDivisionTypeDto) {
    return this.geographyService.createDivisionType(dto);
  }

  @Get('division-types')
  @ApiOperation({ summary: 'Listar tipos de división' })
  findAllDivisionTypes() {
    return this.geographyService.findAllDivisionTypes();
  }

  @Get('division-types/:id')
  @ApiOperation({ summary: 'Obtener tipo de división por id' })
  @ApiParam({ name: 'id', description: 'ID del tipo (cuid)' })
  findDivisionTypeById(@Param('id') id: string) {
    return this.geographyService.findDivisionTypeById(id);
  }

  @Post('administrative-divisions')
  @ApiOperation({ summary: 'Crear división administrativa' })
  createAdministrativeDivision(@Body() dto: CreateAdministrativeDivisionDto) {
    return this.geographyService.createAdministrativeDivision(dto);
  }

  @Get('administrative-divisions')
  @ApiOperation({ summary: 'Listar divisiones administrativas' })
  findAllAdministrativeDivisions() {
    return this.geographyService.findAllAdministrativeDivisions();
  }

  @Get('administrative-divisions/:id')
  @ApiOperation({ summary: 'Obtener división administrativa por id' })
  @ApiParam({ name: 'id', description: 'ID de la división (cuid)' })
  findAdministrativeDivisionById(@Param('id') id: string) {
    return this.geographyService.findAdministrativeDivisionById(id);
  }

  @Patch('administrative-divisions/:id')
  @ApiOperation({ summary: 'Actualizar división administrativa' })
  @ApiParam({ name: 'id', description: 'ID de la división (cuid)' })
  updateAdministrativeDivision(
    @Param('id') id: string,
    @Body() dto: UpdateAdministrativeDivisionDto,
  ) {
    return this.geographyService.updateAdministrativeDivision(id, dto);
  }
}
