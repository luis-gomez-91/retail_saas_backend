# Reemplaza ManyToMany implícitos: Plan↔Modulo solo vía PlanModulo; RolEmpresa↔Modulo vía RolModulo.

import django.db.models.deletion
from django.db import migrations, models


def copiar_modulos_rol_a_rolmodulo(apps, schema_editor):
    RolEmpresa = apps.get_model('core', 'RolEmpresa')
    RolModulo = apps.get_model('core', 'RolModulo')
    filas = []
    for rol in RolEmpresa.objects.all():
        for m in rol.modulos.all():
            filas.append(RolModulo(rol_id=rol.pk, modulo_id=m.pk))
    if filas:
        RolModulo.objects.bulk_create(filas, ignore_conflicts=True)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_alter_cuentafacturacion_options_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='plan',
            name='modulos',
        ),
        migrations.CreateModel(
            name='RolModulo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                (
                    'modulo',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='rol_modulos',
                        to='core.modulo',
                    ),
                ),
                (
                    'rol',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='rol_modulos',
                        to='core.rolempresa',
                    ),
                ),
            ],
            options={
                'verbose_name': 'módulo del rol',
                'verbose_name_plural': 'módulos del rol',
            },
        ),
        migrations.AddConstraint(
            model_name='rolmodulo',
            constraint=models.UniqueConstraint(fields=('rol', 'modulo'), name='uniq_rol_modulo'),
        ),
        migrations.RunPython(copiar_modulos_rol_a_rolmodulo, noop_reverse),
        migrations.RemoveField(
            model_name='rolempresa',
            name='modulos',
        ),
    ]
