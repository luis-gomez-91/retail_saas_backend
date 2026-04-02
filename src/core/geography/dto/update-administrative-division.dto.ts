import { PartialType } from '@nestjs/swagger';
import { CreateAdministrativeDivisionDto } from './create-administrative-division.dto';

export class UpdateAdministrativeDivisionDto extends PartialType(
  CreateAdministrativeDivisionDto,
) {}
