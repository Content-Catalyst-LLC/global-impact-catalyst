from fastapi.testclient import TestClient
from app.main import app

def test_healthz():
    c = TestClient(app)
    assert c.get("/healthz").json() == {"ok": True}
