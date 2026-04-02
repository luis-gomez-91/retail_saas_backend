import {
  Body,
  Controller,
  Delete,
  Get,
  Param,
  Patch,
  Post,
  UseGuards,
} from '@nestjs/common';
import {
  ApiBearerAuth,
  ApiOperation,
  ApiParam,
  ApiTags,
} from '@nestjs/swagger';
import { JwtAuthGuard } from '../auth/guards/jwt-auth.guard';
import {
  AssignPermissionToRoleDto,
  AssignPermissionToUserDto,
  AssignRoleToUserDto,
} from './dto/assign-permission.dto';
import {
  CreateIdentificationTypeDto,
  UpdateIdentificationTypeDto,
} from './dto/create-identification-type.dto';
import {
  CreatePermissionDto,
  UpdatePermissionDto,
} from './dto/create-permission.dto';
import { CreateRoleDto, UpdateRoleDto } from './dto/create-role.dto';
import { RbacService } from './rbac.service';

@ApiTags('rbac')
@ApiBearerAuth()
@UseGuards(JwtAuthGuard)
@Controller('rbac')
export class RbacController {
  constructor(private readonly rbacService: RbacService) {}

  // --- identification-types ---

  @Post('identification-types')
  @ApiOperation({ summary: 'Crear tipo de identificación' })
  createIdentificationType(@Body() dto: CreateIdentificationTypeDto) {
    return this.rbacService.createIdentificationType(dto);
  }

  @Get('identification-types')
  @ApiOperation({ summary: 'Listar tipos de identificación' })
  findAllIdentificationTypes() {
    return this.rbacService.findAllIdentificationTypes();
  }

  @Get('identification-types/:id')
  @ApiOperation({ summary: 'Obtener tipo de identificación' })
  @ApiParam({ name: 'id' })
  findIdentificationTypeById(@Param('id') id: string) {
    return this.rbacService.findIdentificationTypeById(id);
  }

  @Patch('identification-types/:id')
  @ApiOperation({ summary: 'Actualizar tipo de identificación' })
  @ApiParam({ name: 'id' })
  updateIdentificationType(
    @Param('id') id: string,
    @Body() dto: UpdateIdentificationTypeDto,
  ) {
    return this.rbacService.updateIdentificationType(id, dto);
  }

  // --- auth providers ---

  @Get('auth-providers')
  @ApiOperation({ summary: 'Listar proveedores OAuth configurables' })
  findAuthProviders() {
    return this.rbacService.findAllAuthProviders();
  }

  // --- roles ---

  @Post('roles')
  @ApiOperation({ summary: 'Crear rol' })
  createRole(@Body() dto: CreateRoleDto) {
    return this.rbacService.createRole(dto);
  }

  @Get('roles')
  @ApiOperation({ summary: 'Listar roles y sus permisos' })
  findAllRoles() {
    return this.rbacService.findAllRoles();
  }

  @Get('roles/:id')
  @ApiOperation({ summary: 'Obtener rol' })
  @ApiParam({ name: 'id' })
  findRoleById(@Param('id') id: string) {
    return this.rbacService.findRoleById(id);
  }

  @Patch('roles/:id')
  @ApiOperation({ summary: 'Actualizar rol' })
  @ApiParam({ name: 'id' })
  updateRole(@Param('id') id: string, @Body() dto: UpdateRoleDto) {
    return this.rbacService.updateRole(id, dto);
  }

  @Post('roles/:roleId/permissions')
  @ApiOperation({ summary: 'Asociar permiso a rol' })
  @ApiParam({ name: 'roleId' })
  addPermissionToRole(
    @Param('roleId') roleId: string,
    @Body() dto: AssignPermissionToRoleDto,
  ) {
    return this.rbacService.addPermissionToRole(roleId, dto.permissionId);
  }

  @Delete('roles/:roleId/permissions/:permissionId')
  @ApiOperation({ summary: 'Quitar permiso de un rol' })
  @ApiParam({ name: 'roleId' })
  @ApiParam({ name: 'permissionId' })
  removePermissionFromRole(
    @Param('roleId') roleId: string,
    @Param('permissionId') permissionId: string,
  ) {
    return this.rbacService.removePermissionFromRole(roleId, permissionId);
  }

  // --- permissions catalog ---

  @Post('permissions')
  @ApiOperation({ summary: 'Crear permiso' })
  createPermission(@Body() dto: CreatePermissionDto) {
    return this.rbacService.createPermission(dto);
  }

  @Get('permissions')
  @ApiOperation({ summary: 'Listar permisos' })
  findAllPermissions() {
    return this.rbacService.findAllPermissions();
  }

  @Get('permissions/:id')
  @ApiOperation({ summary: 'Obtener permiso' })
  @ApiParam({ name: 'id' })
  findPermissionById(@Param('id') id: string) {
    return this.rbacService.findPermissionById(id);
  }

  @Patch('permissions/:id')
  @ApiOperation({ summary: 'Actualizar permiso' })
  @ApiParam({ name: 'id' })
  updatePermission(@Param('id') id: string, @Body() dto: UpdatePermissionDto) {
    return this.rbacService.updatePermission(id, dto);
  }

  // --- user roles ---

  @Post('users/:userId/roles')
  @ApiOperation({ summary: 'Asignar rol a usuario (tabla auth_user_role)' })
  @ApiParam({ name: 'userId' })
  addRoleToUser(
    @Param('userId') userId: string,
    @Body() dto: AssignRoleToUserDto,
  ) {
    return this.rbacService.addRoleToUser(userId, dto.roleId);
  }

  @Delete('users/:userId/roles/:roleId')
  @ApiOperation({ summary: 'Quitar rol de usuario' })
  @ApiParam({ name: 'userId' })
  @ApiParam({ name: 'roleId' })
  removeRoleFromUser(
    @Param('userId') userId: string,
    @Param('roleId') roleId: string,
  ) {
    return this.rbacService.removeRoleFromUser(userId, roleId);
  }

  // --- user permissions ---

  @Post('users/:userId/permissions')
  @ApiOperation({
    summary: 'Permiso directo por usuario (auth_user_permission)',
    description:
      'Conceder permiso extra o denegar explícitamente (granted: false).',
  })
  @ApiParam({ name: 'userId' })
  addUserPermission(
    @Param('userId') userId: string,
    @Body() dto: AssignPermissionToUserDto,
  ) {
    return this.rbacService.addOrUpdateUserPermission(userId, dto);
  }

  @Delete('users/:userId/permissions/:permissionId')
  @ApiOperation({ summary: 'Eliminar permiso directo de usuario' })
  @ApiParam({ name: 'userId' })
  @ApiParam({ name: 'permissionId' })
  removeUserPermission(
    @Param('userId') userId: string,
    @Param('permissionId') permissionId: string,
  ) {
    return this.rbacService.removeUserPermission(userId, permissionId);
  }

  @Get('users/:userId/effective-permissions')
  @ApiOperation({
    summary: 'Permisos efectivos del usuario',
    description:
      'Unión de permisos por roles más directos concedidos, menos denegaciones explícitas.',
  })
  @ApiParam({ name: 'userId' })
  effectivePermissions(@Param('userId') userId: string) {
    return this.rbacService.effectivePermissionsForUser(userId);
  }
}
