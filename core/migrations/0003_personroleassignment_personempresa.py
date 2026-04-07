# Generated manually: roles ligados a PersonEmpresa

from django.db import migrations, models
import django.db.models.deletion


def forwards_assign_person_empresa(apps, schema_editor):
    PersonRoleAssignment = apps.get_model('core', 'PersonRoleAssignment')
    PersonEmpresa = apps.get_model('core', 'PersonEmpresa')
    for a in PersonRoleAssignment.objects.all().iterator():
        pe = PersonEmpresa.objects.filter(
            person_id=a.person_id,
            empresa_id=a.empresa_id,
        ).first()
        if pe is None:
            pe = PersonEmpresa.objects.create(
                person_id=a.person_id,
                empresa_id=a.empresa_id,
                is_active=True,
            )
        a.person_empresa_id = pe.pk
        a.save(update_fields=['person_empresa_id'])


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_module_icon'),
    ]

    operations = [
        migrations.AddField(
            model_name='personroleassignment',
            name='person_empresa',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='role_assignments',
                to='core.personempresa',
            ),
        ),
        migrations.RunPython(forwards_assign_person_empresa, migrations.RunPython.noop),
        migrations.RemoveConstraint(
            model_name='personroleassignment',
            name='uniq_person_role_scope',
        ),
        migrations.RemoveField(
            model_name='personroleassignment',
            name='person',
        ),
        migrations.RemoveField(
            model_name='personroleassignment',
            name='empresa',
        ),
        migrations.AlterField(
            model_name='personroleassignment',
            name='person_empresa',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='role_assignments',
                to='core.personempresa',
            ),
        ),
        migrations.AddConstraint(
            model_name='personroleassignment',
            constraint=models.UniqueConstraint(
                fields=('person_empresa', 'role', 'organizacion', 'sucursal'),
                name='uniq_personempresa_role_scope',
            ),
        ),
    ]
