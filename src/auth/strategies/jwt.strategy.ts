import { Injectable } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { PassportStrategy } from '@nestjs/passport';
import { ExtractJwt, Strategy } from 'passport-jwt';
import { AuthUserPayload } from '../auth-user.payload';

type JwtPayload = {
  sub: string;
  email: string;
  permissions?: string[];
};

@Injectable()
export class JwtStrategy extends PassportStrategy(Strategy, 'jwt') {
  constructor(config: ConfigService) {
    super({
      jwtFromRequest: ExtractJwt.fromAuthHeaderAsBearerToken(),
      ignoreExpiration: false,
      secretOrKey: config.get<string>('JWT_SECRET') ?? 'cambiar-en-produccion',
    });
  }

  validate(payload: JwtPayload): AuthUserPayload {
    return {
      userId: payload.sub,
      email: payload.email,
      permissions: payload.permissions ?? [],
    };
  }
}
