from django.db import migrations, models
import django.db.models.deletion


def forward_copy_persona(apps, schema_editor):
    RolPersonaEmpresa = apps.get_model('core', 'RolPersonaEmpresa')
    for asignacion in RolPersonaEmpresa.objects.select_related('persona_empresa').all():
        pe = getattr(asignacion, 'persona_empresa', None)
        if pe is not None:
            asignacion.persona_tmp_id = pe.persona_id
            asignacion.save(update_fields=['persona_tmp'])


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0011_rolpersona'),
    ]

    operations = [
        migrations.AddField(
            model_name='rolpersonaempresa',
            name='persona_tmp',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='+',
                to='core.persona',
            ),
        ),
        migrations.RunPython(forward_copy_persona, migrations.RunPython.noop),
        migrations.RemoveConstraint(
            model_name='rolpersonaempresa',
            name='uniq_membresia_rol_alcance',
        ),
        migrations.RemoveField(
            model_name='rolpersonaempresa',
            name='persona_empresa',
        ),
        migrations.RenameField(
            model_name='rolpersonaempresa',
            old_name='persona_tmp',
            new_name='persona',
        ),
        migrations.AlterField(
            model_name='rolpersonaempresa',
            name='persona',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='asignaciones_rol_empresa',
                to='core.persona',
            ),
        ),
        migrations.AddConstraint(
            model_name='rolpersonaempresa',
            constraint=models.UniqueConstraint(
                fields=('persona', 'rol'),
                name='uniq_persona_rol_alcance',
            ),
        ),
    ]
