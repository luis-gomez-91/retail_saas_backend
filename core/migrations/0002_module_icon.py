# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='module',
            name='icon',
            field=models.CharField(
                blank=True,
                default='',
                help_text='Clave del icono en la UI (p. ej. nombre Lucide en PascalCase o kebab-case).',
                max_length=64,
            ),
        ),
    ]
