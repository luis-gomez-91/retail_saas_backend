import { Injectable, NotFoundException } from '@nestjs/common';
import * as bcrypt from 'bcrypt';
import { Prisma } from '@prisma/client';
import { PrismaService } from '../prisma/prisma.service';
import { UpdateUserDto } from './dto/update-user.dto';

const BCRYPT_ROUNDS = 10;

@Injectable()
export class UsersService {
  constructor(private readonly prisma: PrismaService) {}

  findAll() {
    return this.prisma.user.findMany({
      orderBy: { createdAt: 'desc' },
      include: {
        person: {
          include: {
            country: true,
            identificationType: true,
            administrativeDivision: true,
            cityDivision: true,
          },
        },
        userRoles: { include: { role: true } },
      },
      omit: { passwordHash: true },
    });
  }

  async findOne(id: string) {
    const user = await this.prisma.user.findUnique({
      where: { id },
      include: {
        person: {
          include: {
            country: true,
            identificationType: true,
            administrativeDivision: true,
            cityDivision: true,
          },
        },
        userRoles: { include: { role: true } },
        authAccounts: { include: { authProvider: true } },
      },
      omit: { passwordHash: true },
    });
    if (!user) throw new NotFoundException('Usuario no encontrado');
    return user;
  }

  async update(id: string, dto: UpdateUserDto) {
    await this.findOne(id);

    const {
      email,
      password,
      isActive,
      emailVerified,
      firstName,
      lastName,
      identificationTypeId,
      identification,
      birthDate,
      emailInstitutional,
      emailPersonal,
      phone,
      countryId,
      administrativeDivisionId,
      cityDivisionId,
      addressLine1,
      addressLine2,
      postalCode,
      timezone,
      latitude,
      longitude,
      ...rest
    } = dto;

    void rest;

    const userData: Prisma.UserUpdateInput = {};
    if (email !== undefined) userData.email = email.toLowerCase();
    if (password !== undefined) {
      userData.passwordHash = await bcrypt.hash(password, BCRYPT_ROUNDS);
    }
    if (isActive !== undefined) userData.isActive = isActive;
    if (emailVerified !== undefined) userData.emailVerified = emailVerified;

    const personData: Prisma.PersonUpdateInput = {};
    if (firstName !== undefined) personData.firstName = firstName;
    if (lastName !== undefined) personData.lastName = lastName;
    if (identificationTypeId !== undefined) {
      personData.identificationType =
        identificationTypeId === null
          ? { disconnect: true }
          : { connect: { id: identificationTypeId } };
    }
    if (identification !== undefined)
      personData.identification = identification;
    if (birthDate !== undefined) {
      personData.birthDate = birthDate === null ? null : new Date(birthDate);
    }
    if (emailInstitutional !== undefined) {
      personData.emailInstitutional = emailInstitutional;
    }
    if (emailPersonal !== undefined) personData.emailPersonal = emailPersonal;
    if (phone !== undefined) personData.phone = phone;
    if (countryId !== undefined) {
      personData.country =
        countryId === null
          ? { disconnect: true }
          : { connect: { id: countryId } };
    }
    if (administrativeDivisionId !== undefined) {
      personData.administrativeDivision =
        administrativeDivisionId === null
          ? { disconnect: true }
          : { connect: { id: administrativeDivisionId } };
    }
    if (cityDivisionId !== undefined) {
      personData.cityDivision =
        cityDivisionId === null
          ? { disconnect: true }
          : { connect: { id: cityDivisionId } };
    }
    if (addressLine1 !== undefined) personData.addressLine1 = addressLine1;
    if (addressLine2 !== undefined) personData.addressLine2 = addressLine2;
    if (postalCode !== undefined) personData.postalCode = postalCode;
    if (timezone !== undefined) personData.timezone = timezone;
    if (latitude !== undefined) {
      personData.latitude = latitude === null ? null : latitude;
    }
    if (longitude !== undefined) {
      personData.longitude = longitude === null ? null : longitude;
    }

    return this.prisma.$transaction(async (tx) => {
      if (Object.keys(userData).length > 0) {
        await tx.user.update({ where: { id }, data: userData });
      }
      if (Object.keys(personData).length > 0) {
        const u = await tx.user.findUniqueOrThrow({
          where: { id },
          select: { personId: true },
        });
        await tx.person.update({
          where: { id: u.personId },
          data: personData,
        });
      }
      return tx.user.findUniqueOrThrow({
        where: { id },
        include: {
          person: {
            include: {
              country: true,
              identificationType: true,
              administrativeDivision: true,
              cityDivision: true,
            },
          },
          userRoles: { include: { role: true } },
        },
        omit: { passwordHash: true },
      });
    });
  }
}
