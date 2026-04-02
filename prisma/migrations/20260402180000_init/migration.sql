-- CreateSchema
CREATE SCHEMA IF NOT EXISTS "public";

-- CreateTable
CREATE TABLE "core_country" (
    "id" TEXT NOT NULL,
    "name" VARCHAR(100) NOT NULL,
    "code" VARCHAR(2) NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "core_country_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "core_division_type" (
    "id" TEXT NOT NULL,
    "name" VARCHAR(50) NOT NULL,
    "level" INTEGER NOT NULL,
    "countryId" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "core_division_type_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "core_administrative_division" (
    "id" TEXT NOT NULL,
    "name" VARCHAR(100) NOT NULL,
    "code" VARCHAR(10),
    "countryId" TEXT NOT NULL,
    "parentId" TEXT,
    "divisionTypeId" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "core_administrative_division_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "core_division_type_name_countryId_key" ON "core_division_type"("name", "countryId");

-- CreateIndex
CREATE UNIQUE INDEX "core_administrative_division_name_parentId_countryId_key" ON "core_administrative_division"("name", "parentId", "countryId");

-- AddForeignKey
ALTER TABLE "core_division_type" ADD CONSTRAINT "core_division_type_countryId_fkey" FOREIGN KEY ("countryId") REFERENCES "core_country"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "core_administrative_division" ADD CONSTRAINT "core_administrative_division_countryId_fkey" FOREIGN KEY ("countryId") REFERENCES "core_country"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "core_administrative_division" ADD CONSTRAINT "core_administrative_division_parentId_fkey" FOREIGN KEY ("parentId") REFERENCES "core_administrative_division"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "core_administrative_division" ADD CONSTRAINT "core_administrative_division_divisionTypeId_fkey" FOREIGN KEY ("divisionTypeId") REFERENCES "core_division_type"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

