import pytest
from http import HTTPStatus

from api_pedidos.api import app
from fastapi.testclient import TestClient

@pytest.fixture
def client():
    print("tops")
    test_client = TestClient(app)
    return test_client


def test_quando_verificar_integridade_devo_ter_como_retorno_codigo_de_status_200(client):
    response = client.get("/healthcheck")
    assert response.status_code == HTTPStatus.OK

def test_quando_verificar_integridade_formato_de_retorno_deve_ser_json(client):
    response = client.get("/healthcheck")
    assert response.headers["Content-Type"] == "application/json"
    
def test_quando_verificar_integridade_retorno_deve_ser_igual_a_esperado(client):
    response = client.get("/healthcheck")
    assert response.json() == {"status": "ok"}