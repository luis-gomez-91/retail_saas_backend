# UserIdentity.provider_code reemplaza FK a AuthProvider

from django.db import migrations, models


def copy_provider_code(apps, schema_editor):
    UserIdentity = apps.get_model('core', 'UserIdentity')
    AuthProvider = apps.get_model('core', 'AuthProvider')
    for ui in UserIdentity.objects.all().iterator():
        prov = AuthProvider.objects.filter(pk=ui.provider_id).first()
        ui.provider_code = prov.code if prov else 'password'
        ui.save(update_fields=['provider_code'])


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_personroleassignment_personempresa'),
    ]

    operations = [
        migrations.AddField(
            model_name='useridentity',
            name='provider_code',
            field=models.SlugField(
                help_text='p. ej. password, google, oidc',
                max_length=64,
                null=True,
            ),
        ),
        migrations.RunPython(copy_provider_code, migrations.RunPython.noop),
        migrations.RemoveConstraint(
            model_name='useridentity',
            name='uniq_user_provider_uid',
        ),
        migrations.RemoveField(
            model_name='useridentity',
            name='provider',
        ),
        migrations.AlterField(
            model_name='useridentity',
            name='provider_code',
            field=models.SlugField(help_text='p. ej. password, google, oidc', max_length=64),
        ),
        migrations.AddConstraint(
            model_name='useridentity',
            constraint=models.UniqueConstraint(
                fields=('user', 'provider_code', 'provider_uid'),
                name='uniq_user_provider_uid',
            ),
        ),
        migrations.DeleteModel(
            name='AuthProvider',
        ),
    ]
