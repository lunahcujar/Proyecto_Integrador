from fastapi.testclient import TestClient
from app_.main import app

client = TestClient(app)

def test_rutina_usuario_existente(monkeypatch):
    # Simular una respuesta de Supabase para que no dependa del servicio real
    def mock_supabase_query(*args, **kwargs):
        class MockResponse:
            data = [
                {
                    "product_name": "Garnier Micellar Water",
                    "product_type": "Cleanser",
                    "image_url": "https://example.com/img.jpg",
                    "clean_ingreds": "agua, glicerina, etc.",
                    "product_url": "https://example.com/product"
                }
            ]
        return MockResponse()

    monkeypatch.setattr("app_.templates.routes.supabase.table", lambda name: type("MockTable", (), {
        "select": lambda *a, **kw: type("MockQuery", (), {
            "eq": lambda *a, **kw: mock_supabase_query()
        })()
    })())

    response = client.get("/api/rutina?email=juan@hotmail.com")
    assert response.status_code == 200
    data = response.json()
    assert "manana" in data
    assert isinstance(data["manana"], list)
