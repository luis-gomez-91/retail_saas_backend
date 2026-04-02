/** Códigos de permiso persistidos en `auth_permission.code` */
export const PERMISSION_CODES = {
  RBAC_MANAGE: 'rbac.manage',
  USERS_READ: 'users.read',
  USERS_UPDATE: 'users.update',
} as const;

export type PermissionCode =
  (typeof PERMISSION_CODES)[keyof typeof PERMISSION_CODES];
