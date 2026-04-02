import { OmitType } from '@nestjs/swagger';
import { UpdateUserDto } from './update-user.dto';

/** Actualización de perfil propio: sin `isActive` ni `emailVerified`. */
export class UpdateProfileDto extends OmitType(UpdateUserDto, [
  'isActive',
  'emailVerified',
] as const) {}
