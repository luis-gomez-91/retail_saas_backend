import { SetMetadata } from '@nestjs/common';
import {
  REQUIRE_PERMISSIONS_KEY,
  type RequirePermissionsMeta,
} from '../metadata';

export const RequirePermissions = (
  ...permissions: string[]
): ((
  target: object,
  key?: string | symbol,
  descriptor?: PropertyDescriptor,
) => void) => {
  const meta: RequirePermissionsMeta = {
    permissions,
    mode: 'all',
  };
  return SetMetadata(REQUIRE_PERMISSIONS_KEY, meta);
};

/** Requiere al menos uno de los permisos indicados */
export const RequireAnyPermission = (
  ...permissions: string[]
): ((
  target: object,
  key?: string | symbol,
  descriptor?: PropertyDescriptor,
) => void) => {
  const meta: RequirePermissionsMeta = {
    permissions,
    mode: 'any',
  };
  return SetMetadata(REQUIRE_PERMISSIONS_KEY, meta);
};
