import {
  Body,
  Controller,
  Get,
  HttpCode,
  Post,
  Req,
  UseGuards,
} from '@nestjs/common';
import { AuthGuard } from '@nestjs/passport';
import { ApiBearerAuth, ApiBody, ApiOperation, ApiTags } from '@nestjs/swagger';
import type { Request } from 'express';
import { AuthService } from './auth.service';
import { CurrentUser } from './decorators/current-user.decorator';
import { LoginDto } from './dto/login.dto';
import { RegisterDto } from './dto/register.dto';
import { FacebookOAuthGuard } from './guards/facebook-oauth.guard';
import { GoogleOAuthGuard } from './guards/google-oauth.guard';
import { JwtAuthGuard } from './guards/jwt-auth.guard';
import type { AuthUserPayload } from './auth-user.payload';
import type { SafeUser } from './auth.service';

@ApiTags('auth')
@Controller('auth')
export class AuthController {
  constructor(private readonly authService: AuthService) {}

  @Post('register')
  @ApiOperation({ summary: 'Registro con correo y contraseña' })
  register(@Body() dto: RegisterDto) {
    return this.authService.register(dto);
  }

  @Post('login')
  @HttpCode(200)
  @UseGuards(AuthGuard('local'))
  @ApiOperation({ summary: 'Inicio de sesión con correo y contraseña' })
  @ApiBody({ type: LoginDto })
  login(@Req() req: Request & { user: SafeUser }) {
    return this.authService.issueTokensForUserId(req.user.id);
  }

  @Get('me')
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth()
  @ApiOperation({ summary: 'Perfil del usuario autenticado' })
  me(@CurrentUser() user: AuthUserPayload) {
    return this.authService.getProfile(user.userId);
  }

  @Get('google')
  @ApiOperation({
    summary: 'Iniciar OAuth con Google (redirección)',
    description:
      'Requiere GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET y GOOGLE_CALLBACK_URL.',
  })
  @UseGuards(GoogleOAuthGuard)
  googleAuth() {
    /* Passport redirige */
  }

  @Get('google/callback')
  @UseGuards(GoogleOAuthGuard)
  @ApiOperation({ summary: 'Callback OAuth Google' })
  googleCallback(@Req() req: Request & { user: unknown }) {
    return req.user;
  }

  @Get('facebook')
  @ApiOperation({
    summary: 'Iniciar OAuth con Facebook (redirección)',
    description:
      'Requiere FACEBOOK_APP_ID, FACEBOOK_APP_SECRET y FACEBOOK_CALLBACK_URL.',
  })
  @UseGuards(FacebookOAuthGuard)
  facebookAuth() {
    /* Passport redirige */
  }

  @Get('facebook/callback')
  @UseGuards(FacebookOAuthGuard)
  @ApiOperation({ summary: 'Callback OAuth Facebook' })
  facebookCallback(@Req() req: Request & { user: unknown }) {
    return req.user;
  }
}
