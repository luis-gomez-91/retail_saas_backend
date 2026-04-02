import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

const PERMISSION_SEED = [
  {
    code: 'rbac.manage',
    name: 'Administrar RBAC',
    description:
      'Roles, permisos, tipos de documento (mutación) y asignaciones de usuario.',
  },
  {
    code: 'users.read',
    name: 'Ver usuarios',
    description: 'Listar y consultar usuarios.',
  },
  {
    code: 'users.update',
    name: 'Administrar usuarios',
    description:
      'Modificar usuarios (incluye campos administrativos como activación).',
  },
] as const;

async function main() {
  for (const p of [
    { code: 'GOOGLE', name: 'Google' },
    { code: 'FACEBOOK', name: 'Facebook' },
    { code: 'MICROSOFT', name: 'Microsoft' },
    { code: 'APPLE', name: 'Apple' },
  ]) {
    await prisma.authProvider.upsert({
      where: { code: p.code },
      create: p,
      update: { name: p.name },
    });
  }

  for (const t of [
    { code: 'CC', name: 'Cédula de ciudadanía' },
    { code: 'CE', name: 'Cédula de extranjería' },
    { code: 'PASSPORT', name: 'Pasaporte' },
    { code: 'NIT', name: 'NIT' },
  ]) {
    await prisma.identificationType.upsert({
      where: { code: t.code },
      create: t,
      update: { name: t.name },
    });
  }

  for (const perm of PERMISSION_SEED) {
    await prisma.permission.upsert({
      where: { code: perm.code },
      create: perm,
      update: { name: perm.name, description: perm.description },
    });
  }

  const adminRole = await prisma.role.upsert({
    where: { code: 'SUPER_ADMIN' },
    create: {
      code: 'SUPER_ADMIN',
      name: 'Super administrador',
      description: 'Acceso total a RBAC y gestión de usuarios.',
    },
    update: {
      name: 'Super administrador',
      description: 'Acceso total a RBAC y gestión de usuarios.',
    },
  });

  const allPerms = await prisma.permission.findMany({
    where: { code: { in: [...PERMISSION_SEED.map((p) => p.code)] } },
  });

  for (const perm of allPerms) {
    await prisma.rolePermission.upsert({
      where: {
        roleId_permissionId: { roleId: adminRole.id, permissionId: perm.id },
      },
      create: { roleId: adminRole.id, permissionId: perm.id },
      update: {},
    });
  }

  const bootstrapEmail = process.env.BOOTSTRAP_ADMIN_EMAIL?.trim().toLowerCase();
  if (bootstrapEmail) {
    const user = await prisma.user.findUnique({
      where: { email: bootstrapEmail },
    });
    if (user) {
      await prisma.userRole.upsert({
        where: {
          userId_roleId: { userId: user.id, roleId: adminRole.id },
        },
        create: { userId: user.id, roleId: adminRole.id },
        update: {},
      });
      console.log(`Rol SUPER_ADMIN asignado a ${bootstrapEmail}.`);
    } else {
      console.warn(
        `BOOTSTRAP_ADMIN_EMAIL=${bootstrapEmail}: usuario no encontrado; omitiendo asignación.`,
      );
    }
  }
}

main()
  .then(() => {
    console.log('Seed completado.');
  })
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
