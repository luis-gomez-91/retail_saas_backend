import { DynamicModule, Module, Provider, Type } from '@nestjs/common';
import { ConfigModule, ConfigService } from '@nestjs/config';
import { JwtModule } from '@nestjs/jwt';
import type { SignOptions } from 'jsonwebtoken';
import { PassportModule } from '@nestjs/passport';
import { PrismaModule } from '../prisma/prisma.module';
import { AuthController } from './auth.controller';
import { AuthService } from './auth.service';
import { FacebookStrategy } from './strategies/facebook.strategy';
import { GoogleStrategy } from './strategies/google.strategy';
import { JwtStrategy } from './strategies/jwt.strategy';
import { LocalStrategy } from './strategies/local.strategy';

function oauthStrategies(): Type<unknown>[] {
  const list: Type<unknown>[] = [];
  if (process.env.GOOGLE_CLIENT_ID && process.env.GOOGLE_CLIENT_SECRET) {
    list.push(GoogleStrategy);
  }
  if (process.env.FACEBOOK_APP_ID && process.env.FACEBOOK_APP_SECRET) {
    list.push(FacebookStrategy);
  }
  return list;
}

@Module({})
export class AuthModule {
  static forRoot(): DynamicModule {
    const strategies = oauthStrategies();
    return {
      module: AuthModule,
      global: true,
      imports: [
        PrismaModule,
        ConfigModule,
        PassportModule.register({ defaultStrategy: 'jwt' }),
        JwtModule.registerAsync({
          imports: [ConfigModule],
          useFactory: (config: ConfigService) => {
            const expiresIn = (config.get<string>('JWT_EXPIRES_IN') ??
              '7d') as SignOptions['expiresIn'];
            return {
              secret:
                config.get<string>('JWT_SECRET') ?? 'cambiar-en-produccion',
              signOptions: { expiresIn },
            };
          },
          inject: [ConfigService],
        }),
      ],
      controllers: [AuthController],
      providers: [
        AuthService,
        JwtStrategy,
        LocalStrategy,
        ...(strategies as Provider[]),
      ],
      exports: [AuthService, JwtModule],
    };
  }
}
