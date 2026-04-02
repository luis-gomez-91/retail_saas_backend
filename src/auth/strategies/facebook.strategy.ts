import { Injectable } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { PassportStrategy } from '@nestjs/passport';
import { Profile, Strategy } from 'passport-facebook';
import { AuthService } from '../auth.service';

@Injectable()
export class FacebookStrategy extends PassportStrategy(Strategy, 'facebook') {
  constructor(
    config: ConfigService,
    private readonly authService: AuthService,
  ) {
    super({
      clientID: config.getOrThrow<string>('FACEBOOK_APP_ID'),
      clientSecret: config.getOrThrow<string>('FACEBOOK_APP_SECRET'),
      callbackURL:
        config.get<string>('FACEBOOK_CALLBACK_URL') ??
        'http://localhost:3000/auth/facebook/callback',
      profileFields: ['id', 'emails', 'name'],
      scope: ['email'],
    });
  }

  async validate(
    _accessToken: string,
    _refreshToken: string,
    profile: Profile,
    done: (err: Error | null, user?: unknown) => void,
  ): Promise<void> {
    const email = profile.emails?.[0]?.value;
    if (!email) {
      return done(
        new Error(
          'Facebook no devolvió email; conceda el permiso de email en la app',
        ),
        undefined,
      );
    }
    try {
      const payload = await this.authService.findOrCreateOAuthUser({
        providerCode: 'FACEBOOK',
        externalUserId: profile.id,
        email,
        firstName: profile.name?.givenName,
        lastName: profile.name?.familyName,
      });
      done(null, payload);
    } catch (err) {
      done(err as Error, undefined);
    }
  }
}
