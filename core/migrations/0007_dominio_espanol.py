# Renombra modelos y campos al dominio en español (preserva datos).

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('core', '0006_user_is_admin'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='personroleassignment',
            name='uniq_personempresa_role_scope',
        ),
        migrations.RemoveConstraint(
            model_name='personempresa',
            name='uniq_person_empresa',
        ),
        migrations.RemoveConstraint(
            model_name='planmodule',
            name='uniq_plan_module',
        ),
        migrations.RemoveConstraint(
            model_name='empresa',
            name='uniq_empresa_slug_per_account',
        ),
        migrations.RenameModel(old_name='BillingAccount', new_name='CuentaFacturacion'),
        migrations.RenameModel(old_name='SubscriptionStatus', new_name='EstadoSuscripcion'),
        migrations.RenameModel(old_name='Module', new_name='Modulo'),
        migrations.RenameModel(old_name='PlanModule', new_name='PlanModulo'),
        migrations.RenameModel(old_name='Subscription', new_name='Suscripcion'),
        migrations.RenameModel(old_name='Role', new_name='RolEmpresa'),
        migrations.RenameModel(old_name='Person', new_name='Persona'),
        migrations.RenameModel(old_name='PersonEmpresa', new_name='PersonaEmpresa'),
        migrations.RenameModel(old_name='PersonRoleAssignment', new_name='RolPersonaEmpresa'),
        migrations.RenameField(
            model_name='cuentafacturacion',
            old_name='name',
            new_name='nombre',
        ),
        migrations.RenameField(
            model_name='cuentafacturacion',
            old_name='created_at',
            new_name='creado_en',
        ),
        migrations.RenameField(model_name='estadosuscripcion', old_name='code', new_name='codigo'),
        migrations.RenameField(model_name='estadosuscripcion', old_name='name', new_name='nombre'),
        migrations.RenameField(model_name='estadosuscripcion', old_name='is_active', new_name='activo'),
        migrations.RenameField(model_name='estadosuscripcion', old_name='sort_order', new_name='orden'),
        migrations.RenameField(model_name='modulo', old_name='code', new_name='codigo'),
        migrations.RenameField(model_name='modulo', old_name='name', new_name='nombre'),
        migrations.RenameField(model_name='modulo', old_name='description', new_name='descripcion'),
        migrations.RenameField(model_name='modulo', old_name='icon', new_name='icono'),
        migrations.RenameField(model_name='plan', old_name='code', new_name='codigo'),
        migrations.RenameField(model_name='plan', old_name='name', new_name='nombre'),
        migrations.RenameField(model_name='plan', old_name='is_public', new_name='publico'),
        migrations.RenameField(model_name='plan', old_name='display_order', new_name='orden_presentacion'),
        migrations.RenameField(model_name='plan', old_name='modules', new_name='modulos'),
        migrations.RenameField(model_name='planmodulo', old_name='module', new_name='modulo'),
        migrations.RenameField(
            model_name='suscripcion',
            old_name='billing_account',
            new_name='cuenta_facturacion',
        ),
        migrations.RenameField(model_name='suscripcion', old_name='status', new_name='estado'),
        migrations.RenameField(
            model_name='suscripcion',
            old_name='current_period_end',
            new_name='fin_periodo_actual',
        ),
        migrations.RenameField(
            model_name='suscripcion',
            old_name='external_subscription_id',
            new_name='id_suscripcion_externa',
        ),
        migrations.RenameField(model_name='suscripcion', old_name='created_at', new_name='creado_en'),
        migrations.RenameField(model_name='suscripcion', old_name='updated_at', new_name='actualizado_en'),
        migrations.RenameField(model_name='rolempresa', old_name='code', new_name='codigo'),
        migrations.RenameField(model_name='rolempresa', old_name='name', new_name='nombre'),
        migrations.RenameField(model_name='rolempresa', old_name='modules', new_name='modulos'),
        migrations.RenameField(model_name='persona', old_name='user', new_name='usuario'),
        migrations.RenameField(model_name='persona', old_name='name', new_name='nombre'),
        migrations.RenameField(model_name='persona', old_name='last_name', new_name='apellido_paterno'),
        migrations.RenameField(model_name='persona', old_name='second_last_name', new_name='apellido_materno'),
        migrations.RenameField(model_name='persona', old_name='personal_email', new_name='correo_personal'),
        migrations.RenameField(model_name='persona', old_name='phone', new_name='telefono'),
        migrations.RenameField(model_name='persona', old_name='created_at', new_name='creado_en'),
        migrations.RenameField(model_name='persona', old_name='updated_at', new_name='actualizado_en'),
        migrations.RenameField(model_name='personaempresa', old_name='person', new_name='persona'),
        migrations.RenameField(model_name='personaempresa', old_name='is_active', new_name='activa'),
        migrations.RenameField(model_name='personaempresa', old_name='invited_at', new_name='invitado_en'),
        migrations.RenameField(model_name='personaempresa', old_name='joined_at', new_name='ingreso_en'),
        migrations.RenameField(
            model_name='rolpersonaempresa',
            old_name='person_empresa',
            new_name='membresia',
        ),
        migrations.RenameField(model_name='rolpersonaempresa', old_name='role', new_name='rol'),
        migrations.RenameField(
            model_name='empresa',
            old_name='billing_account',
            new_name='cuenta_facturacion',
        ),
        migrations.RenameField(model_name='empresa', old_name='name', new_name='nombre'),
        migrations.RenameField(model_name='empresa', old_name='created_at', new_name='creado_en'),
        migrations.RenameField(model_name='empresa', old_name='updated_at', new_name='actualizado_en'),
        migrations.RenameField(model_name='organizacion', old_name='name', new_name='nombre'),
        migrations.RenameField(model_name='organizacion', old_name='created_at', new_name='creado_en'),
        migrations.RenameField(model_name='organizacion', old_name='updated_at', new_name='actualizado_en'),
        migrations.RenameField(model_name='sucursal', old_name='name', new_name='nombre'),
        migrations.RenameField(model_name='sucursal', old_name='created_at', new_name='creado_en'),
        migrations.RenameField(model_name='sucursal', old_name='updated_at', new_name='actualizado_en'),
        migrations.RenameField(model_name='usuario', old_name='username', new_name='nombre_usuario'),
        migrations.RenameField(model_name='usuario', old_name='date_joined', new_name='fecha_registro'),
        migrations.RenameField(model_name='usuario', old_name='is_staff', new_name='es_staff'),
        migrations.RenameField(model_name='usuario', old_name='is_admin', new_name='es_administrador'),
        migrations.AddConstraint(
            model_name='personaempresa',
            constraint=models.UniqueConstraint(
                fields=('persona', 'empresa'),
                name='uniq_persona_empresa',
            ),
        ),
        migrations.AddConstraint(
            model_name='planmodulo',
            constraint=models.UniqueConstraint(
                fields=('plan', 'modulo'),
                name='uniq_plan_modulo',
            ),
        ),
        migrations.AddConstraint(
            model_name='empresa',
            constraint=models.UniqueConstraint(
                fields=('cuenta_facturacion', 'slug'),
                name='uniq_empresa_slug_per_account',
            ),
        ),
        migrations.AddConstraint(
            model_name='rolpersonaempresa',
            constraint=models.UniqueConstraint(
                fields=('membresia', 'rol', 'organizacion', 'sucursal'),
                name='uniq_membresia_rol_alcance',
            ),
        ),
    ]
