import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';
import { IsBoolean, IsOptional, IsUUID } from 'class-validator';

export class AssignPermissionToRoleDto {
  @ApiProperty()
  @IsUUID()
  permissionId!: string;
}

export class AssignRoleToUserDto {
  @ApiProperty()
  @IsUUID()
  roleId!: string;
}

export class AssignPermissionToUserDto {
  @ApiProperty()
  @IsUUID()
  permissionId!: string;

  @ApiPropertyOptional({
    description:
      'true = conceder permiso adicional; false = denegación explícita (anula rol)',
    default: true,
  })
  @IsOptional()
  @IsBoolean()
  granted?: boolean;
}
