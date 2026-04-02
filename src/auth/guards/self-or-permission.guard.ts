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
  SELF_OR_PERMISSION_KEY,
  type SelfOrPermissionMeta,
} from '../metadata';

@Injectable()
export class SelfOrPermissionGuard implements CanActivate {
  constructor(private readonly reflector: Reflector) {}

  canActivate(context: ExecutionContext): boolean {
    const isPublic = this.reflector.getAllAndOverride<boolean>(IS_PUBLIC_KEY, [
      context.getHandler(),
      context.getClass(),
    ]);
    if (isPublic) {
      return true;
    }

    const meta = this.reflector.getAllAndOverride<SelfOrPermissionMeta>(
      SELF_OR_PERMISSION_KEY,
      [context.getHandler(), context.getClass()],
    );
    if (!meta) {
      return true;
    }

    const request = context.switchToHttp().getRequest<{
      user: AuthUserPayload | undefined;
      params: Record<string, string>;
    }>();
    const user = request.user;
    if (!user?.userId) {
      throw new ForbiddenException('Permisos insuficientes');
    }

    const targetId = request.params[meta.paramKey];
    if (targetId && user.userId === targetId) {
      return true;
    }

    const perms = user.permissions ?? [];
    if (perms.includes(meta.permission)) {
      return true;
    }

    throw new ForbiddenException('Permisos insuficientes');
  }
}
