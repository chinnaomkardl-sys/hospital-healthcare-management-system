import os
import sys
# Ensure parent directory is on sys.path so package imports work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE','hospital_management_system.settings')
import django
print('sys.path[0..5]:', sys.path[:6])
import pathlib
print('cwd:', pathlib.Path.cwd())
print('parent listing:', list(pathlib.Path(sys.path[0]).parent.glob('*'))[:10])
try:
    django.setup()
except Exception as e:
    print('django.setup() error:', e)
    raise
from django.test import Client
from django.urls import resolve
from django.contrib.auth.models import AnonymousUser

c = Client()
resp = c.get('/nurses/patients/')
print('status_code:', resp.status_code)
print('redirect_chain:', resp.redirect_chain)
print('content_snippet:', resp.content.decode(errors='replace')[:1000])
try:
    r = resolve('/nurses/patients/')
    print('resolver_func:', r.func)
    print('view_name:', r.view_name)
except Exception as e:
    print('resolve_error:', e)

u = AnonymousUser()
print('anonymous_has_role_attr:', hasattr(u, 'role'))
print('anonymous_getattr_role:', getattr(u, 'role', None))
