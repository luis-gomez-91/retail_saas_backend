import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';
import { Type } from 'class-transformer';
import {
  IsInt,
  IsOptional,
  IsString,
  MaxLength,
  Min,
  MinLength,
} from 'class-validator';

export class CreateDivisionTypeDto {
  @ApiProperty({ example: 'Provincia', maxLength: 50 })
  @IsString()
  @MaxLength(50)
  name: string;

  @ApiProperty({ example: 1, minimum: 1, description: 'Orden jerárquico' })
  @Type(() => Number)
  @IsInt()
  @Min(1)
  level: number;

  @ApiPropertyOptional({
    description: 'Si se omite, el tipo es global al catálogo',
  })
  @IsOptional()
  @IsString()
  @MinLength(1)
  countryId?: string;
}
