"""Helpers drf-spectacular: agrupa endpoints por tag en OpenAPI."""

from drf_spectacular.utils import extend_schema, extend_schema_view

TAG_USUARIOS = 'Usuarios y personas'
TAG_CATALOGO = 'Catálogo y RBAC'
TAG_FACTURACION = 'Facturación y suscripciones'
TAG_TENANCY = 'Tenancy'


def tag_read_only(tag: str):
    s = extend_schema(tags=[tag])
    return extend_schema_view(list=s, retrieve=s)


def tag_model_viewset(tag: str):
    s = extend_schema(tags=[tag])
    return extend_schema_view(
        list=s,
        create=s,
        retrieve=s,
        update=s,
        partial_update=s,
        destroy=s,
    )
