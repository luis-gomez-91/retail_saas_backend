import { Body, Controller, Get, Param, Patch, UseGuards } from '@nestjs/common';
import {
  ApiBearerAuth,
  ApiOperation,
  ApiParam,
  ApiTags,
} from '@nestjs/swagger';
import type { AuthUserPayload } from '../auth/auth-user.payload';
import { CurrentUser } from '../auth/decorators/current-user.decorator';
import { RequirePermissions } from '../auth/decorators/require-permissions.decorator';
import { SelfOrPermission } from '../auth/decorators/self-or-permission.decorator';
import { JwtAuthGuard } from '../auth/guards/jwt-auth.guard';
import { PermissionsGuard } from '../auth/guards/permissions.guard';
import { SelfOrPermissionGuard } from '../auth/guards/self-or-permission.guard';
import { PERMISSION_CODES } from '../common/permission-codes';
import { UpdateProfileDto } from './dto/update-profile.dto';
import { UpdateUserDto } from './dto/update-user.dto';
import { UsersService } from './users.service';

@ApiTags('users')
@ApiBearerAuth()
@UseGuards(JwtAuthGuard)
@Controller('users')
export class UsersController {
  constructor(private readonly usersService: UsersService) {}

  @Get()
  @UseGuards(PermissionsGuard)
  @RequirePermissions(PERMISSION_CODES.USERS_READ)
  @ApiOperation({ summary: 'Listar usuarios' })
  findAll() {
    return this.usersService.findAll();
  }

  @Get('me')
  @ApiOperation({
    summary:
      'Obtener mi usuario (misma información que GET /users/:id para el perfil propio)',
  })
  findMe(@CurrentUser() user: AuthUserPayload) {
    return this.usersService.findOne(user.userId);
  }

  @Patch('me')
  @ApiOperation({
    summary: 'Actualizar mi perfil',
    description:
      'No permite modificar `isActive` ni `emailVerified` (solo administración).',
  })
  updateMe(
    @CurrentUser() user: AuthUserPayload,
    @Body() dto: UpdateProfileDto,
  ) {
    return this.usersService.update(user.userId, dto);
  }

  @Get(':id')
  @UseGuards(SelfOrPermissionGuard)
  @SelfOrPermission(PERMISSION_CODES.USERS_READ, 'id')
  @ApiOperation({ summary: 'Obtener usuario por id' })
  @ApiParam({ name: 'id', description: 'ID del usuario (UUID)' })
  findOne(@Param('id') id: string) {
    return this.usersService.findOne(id);
  }

  @Patch(':id')
  @UseGuards(SelfOrPermissionGuard)
  @SelfOrPermission(PERMISSION_CODES.USERS_UPDATE, 'id')
  @ApiOperation({ summary: 'Actualizar usuario y datos de persona' })
  @ApiParam({ name: 'id', description: 'ID del usuario (UUID)' })
  update(
    @Param('id') id: string,
    @Body() dto: UpdateUserDto,
    @CurrentUser() actor: AuthUserPayload,
  ) {
    const hasAdminUpdate = actor.permissions?.includes(
      PERMISSION_CODES.USERS_UPDATE,
    );
    const payload = hasAdminUpdate ? dto : stripPrivilegedUserFields(dto);
    return this.usersService.update(id, payload);
  }
}

function stripPrivilegedUserFields(dto: UpdateUserDto): UpdateUserDto {
  const { isActive, emailVerified, ...rest } = dto;
  void isActive;
  void emailVerified;
  return rest;
}
