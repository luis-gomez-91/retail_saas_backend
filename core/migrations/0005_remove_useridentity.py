from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_remove_authprovider'),
    ]

    operations = [
        migrations.DeleteModel(name='UserIdentity'),
    ]
