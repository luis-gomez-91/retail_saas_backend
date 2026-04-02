import {
  CanActivate,
  ExecutionContext,
  ForbiddenException,
  Injectable,
} from '@nestjs/common';
import { Reflector } from '@nestjs/core';
import type { AuthUserPayload } from '../auth-user.payload';
import {
  IS_PUBLIC_KEY,
  REQUIRE_PERMISSIONS_KEY,
  type RequirePermissionsMeta,
} from '../metadata';

@Injectable()
export class PermissionsGuard implements CanActivate {
  constructor(private readonly reflector: Reflector) {}

  canActivate(context: ExecutionContext): boolean {
    const isPublic = this.reflector.getAllAndOverride<boolean>(IS_PUBLIC_KEY, [
      context.getHandler(),
      context.getClass(),
    ]);
    if (isPublic) {
      return true;
    }

    const meta = this.reflector.getAllAndOverride<RequirePermissionsMeta>(
      REQUIRE_PERMISSIONS_KEY,
      [context.getHandler(), context.getClass()],
    );

    if (!meta?.permissions?.length) {
      return true;
    }

    const request = context
      .switchToHttp()
      .getRequest<{ user: AuthUserPayload | undefined }>();
    const user = request.user;
    const userPerms = user?.permissions ?? [];
    const { permissions, mode } = meta;
    const ok =
      mode === 'any'
        ? permissions.some((p) => userPerms.includes(p))
        : permissions.every((p) => userPerms.includes(p));

    if (!ok) {
      throw new ForbiddenException('Permisos insuficientes');
    }
    return true;
  }
}
