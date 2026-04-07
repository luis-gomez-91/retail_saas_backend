from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_remove_useridentity'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='is_admin',
            field=models.BooleanField(
                default=False,
                help_text='Operador: ve módulos de gestión tenant (personas, roles, empresas, etc.).',
                verbose_name='administrator',
            ),
        ),
    ]
