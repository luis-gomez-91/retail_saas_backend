import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

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
