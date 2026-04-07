"""Campos del modelo de usuario en inglés (convención Django)."""

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_dominio_espanol'),
    ]

    operations = [
        migrations.RenameField(
            model_name='usuario',
            old_name='nombre_usuario',
            new_name='username',
        ),
        migrations.RenameField(
            model_name='usuario',
            old_name='fecha_registro',
            new_name='date_joined',
        ),
        migrations.RenameField(
            model_name='usuario',
            old_name='es_staff',
            new_name='is_staff',
        ),
        migrations.RenameField(
            model_name='usuario',
            old_name='es_administrador',
            new_name='is_admin',
        ),
    ]
