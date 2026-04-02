import { SetMetadata } from '@nestjs/common';
import { SELF_OR_PERMISSION_KEY, type SelfOrPermissionMeta } from '../metadata';

/** Permite acceso si `request.user.userId === request.params[paramKey]` o si tiene el permiso. */
export const SelfOrPermission = (
  permission: string,
  paramKey = 'id',
): ((
  target: object,
  key?: string | symbol,
  descriptor?: PropertyDescriptor,
) => void) => {
  const meta: SelfOrPermissionMeta = { permission, paramKey };
  return SetMetadata(SELF_OR_PERMISSION_KEY, meta);
};
