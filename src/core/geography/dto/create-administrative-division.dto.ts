import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';
import { IsOptional, IsString, MaxLength, MinLength } from 'class-validator';

export class CreateAdministrativeDivisionDto {
  @ApiProperty({ example: 'Pichincha', maxLength: 100 })
  @IsString()
  @MaxLength(100)
  name: string;

  @ApiPropertyOptional({ example: '17', maxLength: 10 })
  @IsOptional()
  @IsString()
  @MaxLength(10)
  code?: string;

  @ApiProperty({ description: 'ID del país' })
  @IsString()
  @MinLength(1)
  countryId: string;

  @ApiPropertyOptional({
    description: 'ID de la división padre (omitir para nivel 1)',
  })
  @IsOptional()
  @IsString()
  @MinLength(1)
  parentId?: string;

  @ApiProperty({ description: 'ID del tipo de división' })
  @IsString()
  @MinLength(1)
  divisionTypeId: string;
}
