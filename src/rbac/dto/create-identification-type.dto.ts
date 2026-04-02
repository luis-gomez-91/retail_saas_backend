import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';
import { IsOptional, IsString, MaxLength } from 'class-validator';

export class CreateIdentificationTypeDto {
  @ApiProperty({ example: 'TI' })
  @IsString()
  @MaxLength(32)
  code!: string;

  @ApiProperty({ example: 'Tarjeta de identidad' })
  @IsString()
  @MaxLength(80)
  name!: string;
}

export class UpdateIdentificationTypeDto {
  @ApiPropertyOptional()
  @IsOptional()
  @IsString()
  @MaxLength(32)
  code?: string;

  @ApiPropertyOptional()
  @IsOptional()
  @IsString()
  @MaxLength(80)
  name?: string;
}
