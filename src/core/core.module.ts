import { Module } from '@nestjs/common';
import { GeographyModule } from './geography/geography.module';

@Module({
  imports: [GeographyModule],
  exports: [GeographyModule],
})
export class CoreModule {}
