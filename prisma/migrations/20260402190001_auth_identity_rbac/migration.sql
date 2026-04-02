-- CreateTable
CREATE TABLE "auth_provider" (
    "id" TEXT NOT NULL,
    "code" VARCHAR(32) NOT NULL,
    "name" VARCHAR(80) NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "auth_provider_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "auth_identification_type" (
    "id" TEXT NOT NULL,
    "code" VARCHAR(32) NOT NULL,
    "name" VARCHAR(80) NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "auth_identification_type_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "auth_person" (
    "id" TEXT NOT NULL,
    "first_name" VARCHAR(100) NOT NULL,
    "last_name" VARCHAR(100) NOT NULL,
    "identification" VARCHAR(64),
    "identification_type_id" TEXT,
    "birth_date" DATE,
    "email_institutional" VARCHAR(255),
    "email_personal" VARCHAR(255),
    "phone" VARCHAR(40),
    "country_id" TEXT,
    "administrative_division_id" TEXT,
    "city_division_id" TEXT,
    "address_line1" VARCHAR(255),
    "address_line2" VARCHAR(255),
    "postal_code" VARCHAR(20),
    "timezone" VARCHAR(64),
    "latitude" DECIMAL(10,7),
    "longitude" DECIMAL(10,7),
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "auth_person_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "auth_user" (
    "id" TEXT NOT NULL,
    "email" VARCHAR(255) NOT NULL,
    "password_hash" VARCHAR(255),
    "is_active" BOOLEAN NOT NULL DEFAULT true,
    "email_verified" BOOLEAN NOT NULL DEFAULT false,
    "person_id" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "auth_user_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "auth_user_auth_account" (
    "id" TEXT NOT NULL,
    "user_id" TEXT NOT NULL,
    "auth_provider_id" TEXT NOT NULL,
    "external_user_id" VARCHAR(255) NOT NULL,
    "email_at_link" VARCHAR(255),
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "auth_user_auth_account_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "auth_role" (
    "id" TEXT NOT NULL,
    "code" VARCHAR(64) NOT NULL,
    "name" VARCHAR(120) NOT NULL,
    "description" VARCHAR(500),
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "auth_role_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "auth_permission" (
    "id" TEXT NOT NULL,
    "code" VARCHAR(128) NOT NULL,
    "name" VARCHAR(120) NOT NULL,
    "description" VARCHAR(500),
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "auth_permission_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "auth_role_permission" (
    "role_id" TEXT NOT NULL,
    "permission_id" TEXT NOT NULL,

    CONSTRAINT "auth_role_permission_pkey" PRIMARY KEY ("role_id","permission_id")
);

-- CreateTable
CREATE TABLE "auth_user_role" (
    "user_id" TEXT NOT NULL,
    "role_id" TEXT NOT NULL,

    CONSTRAINT "auth_user_role_pkey" PRIMARY KEY ("user_id","role_id")
);

-- CreateTable
CREATE TABLE "auth_user_permission" (
    "user_id" TEXT NOT NULL,
    "permission_id" TEXT NOT NULL,
    "granted" BOOLEAN NOT NULL DEFAULT true,

    CONSTRAINT "auth_user_permission_pkey" PRIMARY KEY ("user_id","permission_id")
);

-- CreateIndex
CREATE UNIQUE INDEX "auth_provider_code_key" ON "auth_provider"("code");

-- CreateIndex
CREATE UNIQUE INDEX "auth_identification_type_code_key" ON "auth_identification_type"("code");

-- CreateIndex
CREATE UNIQUE INDEX "auth_user_email_key" ON "auth_user"("email");

-- CreateIndex
CREATE UNIQUE INDEX "auth_user_person_id_key" ON "auth_user"("person_id");

-- CreateIndex
CREATE UNIQUE INDEX "auth_user_auth_account_auth_provider_id_external_user_id_key" ON "auth_user_auth_account"("auth_provider_id", "external_user_id");

-- CreateIndex
CREATE UNIQUE INDEX "auth_role_code_key" ON "auth_role"("code");

-- CreateIndex
CREATE UNIQUE INDEX "auth_permission_code_key" ON "auth_permission"("code");

-- AddForeignKey
ALTER TABLE "auth_person" ADD CONSTRAINT "auth_person_identification_type_id_fkey" FOREIGN KEY ("identification_type_id") REFERENCES "auth_identification_type"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "auth_person" ADD CONSTRAINT "auth_person_country_id_fkey" FOREIGN KEY ("country_id") REFERENCES "core_country"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "auth_person" ADD CONSTRAINT "auth_person_administrative_division_id_fkey" FOREIGN KEY ("administrative_division_id") REFERENCES "core_administrative_division"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "auth_person" ADD CONSTRAINT "auth_person_city_division_id_fkey" FOREIGN KEY ("city_division_id") REFERENCES "core_administrative_division"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "auth_user" ADD CONSTRAINT "auth_user_person_id_fkey" FOREIGN KEY ("person_id") REFERENCES "auth_person"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "auth_user_auth_account" ADD CONSTRAINT "auth_user_auth_account_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "auth_user"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "auth_user_auth_account" ADD CONSTRAINT "auth_user_auth_account_auth_provider_id_fkey" FOREIGN KEY ("auth_provider_id") REFERENCES "auth_provider"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "auth_role_permission" ADD CONSTRAINT "auth_role_permission_role_id_fkey" FOREIGN KEY ("role_id") REFERENCES "auth_role"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "auth_role_permission" ADD CONSTRAINT "auth_role_permission_permission_id_fkey" FOREIGN KEY ("permission_id") REFERENCES "auth_permission"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "auth_user_role" ADD CONSTRAINT "auth_user_role_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "auth_user"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "auth_user_role" ADD CONSTRAINT "auth_user_role_role_id_fkey" FOREIGN KEY ("role_id") REFERENCES "auth_role"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "auth_user_permission" ADD CONSTRAINT "auth_user_permission_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "auth_user"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "auth_user_permission" ADD CONSTRAINT "auth_user_permission_permission_id_fkey" FOREIGN KEY ("permission_id") REFERENCES "auth_permission"("id") ON DELETE CASCADE ON UPDATE CASCADE;
