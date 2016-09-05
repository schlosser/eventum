import pytest


@pytest.yield_fixture(scope="function")
def client(eventum):
    yield eventum.app.test_client()


@pytest.yield_fixture(scope="function")
def admin_session(client):
    with client.session_transaction() as session:
        session["gplus_id"] = "admin123"
        yield session


@pytest.mark.parametrize("url", [
    "/admin/media", "/admin/home", "/admin/events", "admin/posts",
    "/admin/users",
])
def test_admin_routes_ok(client, admin_session, url):
    assert client.get(url).status_code == 200


def test_admin_routes_permissions(client):
    assert client.get("/admin").status_code == 301


def test_admin_routes_redirect(client, admin_session):
    assert client.get("/admin").status_code == 301
    assert client.get("/admin/users/me").status_code == 302
