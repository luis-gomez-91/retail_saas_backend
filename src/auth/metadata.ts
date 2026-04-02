export const IS_PUBLIC_KEY = 'auth:public';
export const REQUIRE_PERMISSIONS_KEY = 'auth:require-permissions';
export const SELF_OR_PERMISSION_KEY = 'auth:self-or-permission';

export type RequirePermissionsMeta = {
  permissions: string[];
  mode: 'all' | 'any';
};

export type SelfOrPermissionMeta = {
  permission: string;
  paramKey: string;
};
