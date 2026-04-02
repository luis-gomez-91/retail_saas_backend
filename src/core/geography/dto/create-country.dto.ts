import { ApiProperty } from '@nestjs/swagger';
import { IsString, Length, MaxLength } from 'class-validator';

export class CreateCountryDto {
  @ApiProperty({ example: 'Ecuador', maxLength: 100 })
  @IsString()
  @MaxLength(100)
  name: string;

  @ApiProperty({
    example: 'EC',
    description: 'ISO 3166-1 alpha-2',
    minLength: 2,
    maxLength: 2,
  })
  @IsString()
  @Length(2, 2)
  code: string;
}
