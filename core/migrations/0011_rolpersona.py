# Tabla explícita para asignación rol ↔ persona (modelo RolPersona).

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_rolmodulo_plan_sin_m2m'),
    ]

    operations = [
        migrations.CreateModel(
            name='RolPersona',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                (
                    'persona_empresa',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='persona',
                        to='core.persona',
                    ),
                ),
                (
                    'rol',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='asignaciones_persona',
                        to='core.rolempresa',
                    ),
                ),
            ],
            options={
                'verbose_name': 'asignación rol persona',
                'verbose_name_plural': 'asignaciones rol persona',
            },
        ),
        migrations.AddConstraint(
            model_name='rolpersona',
            constraint=models.UniqueConstraint(fields=('persona_empresa', 'rol'), name='uniq_persona_rol'),
        ),
    ]
