import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { AppController } from './app.controller';
import { AuthModule } from './auth/auth.module';
import { BillingModule } from './billing/billing.module';
import { CommerceModule } from './commerce/commerce.module';
import { CoreModule } from './core/core.module';
import { CrmModule } from './crm/crm.module';
import { IntegrationModule } from './integration/integration.module';
import { NotificationModule } from './notification/notification.module';
import { PaymentsModule } from './payments/payments.module';
import { PrismaModule } from './prisma/prisma.module';
import { QueryModule } from './query/query.module';
import { RbacModule } from './rbac/rbac.module';
import { UsersModule } from './users/users.module';

@Module({
  imports: [
    ConfigModule.forRoot({ isGlobal: true }),
    PrismaModule,
    AuthModule.forRoot(),
    UsersModule,
    RbacModule,
    CoreModule,
    CommerceModule,
    PaymentsModule,
    CrmModule,
    IntegrationModule,
    NotificationModule,
    BillingModule,
    QueryModule,
  ],
  controllers: [AppController],
})
export class AppModule {}
