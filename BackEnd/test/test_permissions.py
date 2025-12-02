import os
import json

# enable test mode for permissionsFunctions
os.environ['TEST_MODE'] = '1'

from Directions import app
import BackEnd.Functions.permissionsFunctions as permFuncs
import BackEnd.GlobalInfo.permissions as permMiddleware


def setup_module(module):
    # ensure default dataset
    permFuncs.fnReplacePermissions([
        {"action": "create", "roles": ["author", "admin"]},
        {"action": "approve", "roles": ["revisor", "PO", "admin"]}
    ])


def test_get_permissions():
    client = app.test_client()
    r = client.get('/api/permissions')
    assert r.status_code == 200
    data = r.get_json()
    assert 'data' in data
    assert any(p['action'] == 'create' for p in data['data'])


def test_put_permissions_requires_admin():
    client = app.test_client()
    payload = {"data": [{"action": "edit", "roles": ["author"]}]}
    # without roles header -> 401
    r = client.put('/api/permissions', json=payload)
    assert r.status_code in (401, 403)

    # with non-admin -> 403
    r = client.put('/api/permissions', json=payload, headers={'X-User-Roles': 'author'})
    assert r.status_code == 403

    # with admin -> 200
    r = client.put('/api/permissions', json=payload, headers={'X-User-Roles': 'admin'})
    assert r.status_code == 200
    body = r.get_json()
    assert 'data' in body


def test_requireAction_middleware_allows_and_denies():
    client = app.test_client()

    # register a test route protected by requireAction('create')
    @app.route('/_test_protected')
    @permMiddleware.requireAction('create')
    def _test_protected():
        return json.dumps({'ok': True}), 200

    # author should be allowed
    r = client.get('/_test_protected', headers={'X-User-Roles': 'author'})
    assert r.status_code == 200

    # revisor not allowed
    r = client.get('/_test_protected', headers={'X-User-Roles': 'revisor'})
    assert r.status_code == 403
