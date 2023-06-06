import pytest
from http import HTTPStatus
from fastapi.testclient import TestClient
from uuid import UUID


from api_pedidos.api import app, recuperar_itens_por_pedido
from api_pedidos.schema import Item
from api_pedidos.excecao import PedidoNaoEncontradoError, FalhaDeComunicacaoError


@pytest.fixture
def client():
    test_client = TestClient(app)
    return test_client


@pytest.fixture
def sobreescreve_recupera_itens_por_pedido():
    def _sobreescreve_recupera_itens_por_pedido(itens_ou_erro):
        def duble(order_id: UUID) -> list[Item]:
            if isinstance(itens_ou_erro, Exception):
                raise itens_ou_erro
            return itens_ou_erro

        app.dependency_overrides[recuperar_itens_por_pedido] = duble

    yield _sobreescreve_recupera_itens_por_pedido
    app.dependency_overrides.clear()


class TestHealthCheck:
    def test_devo_ter_como_retorno_codigo_de_status_200(self, client):
        response = client.get("/healthcheck")
        assert response.status_code == HTTPStatus.OK

    def test_formato_de_retorno_deve_ser_json(self, client):
        response = client.get("/healthcheck")
        assert response.headers["Content-Type"] == "application/json"

    def test_deve_conter_informacoes(self, client):
        response = client.get("/healthcheck")
        assert response.json() == {"status": "ok"}


class TestListarPedidos:
    def test_quando_identificacao_do_pedido_invalido_um_erro_deve_ser_retornado(
        self,
        client,
    ):
        response = client.get("/orders/valor-invalido/items")
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_quando_pedido_nao_encontrado_um_erro_deve_ser_retornado(
        self, client, sobreescreve_recupera_itens_por_pedido
    ):
        sobreescreve_recupera_itens_por_pedido(PedidoNaoEncontradoError())
        response = client.get("/orders/00000000-0000-0000-0000-000000000000/items")
        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_quando_encontrar_pedido_codigo_ok_deve_ser_retornado(
        self, client, sobreescreve_recupera_itens_por_pedido
    ):
        sobreescreve_recupera_itens_por_pedido([])
        resposta = client.get("/orders/7e290683-d67b-4f96-a940-44bef1f69d21/items")
        assert resposta.status_code == HTTPStatus.OK

    def test_quando_encontrar_pedido_deve_retornar_itens(
        self, client, sobreescreve_recupera_itens_por_pedido
    ):
        itens = [
            Item(
                sku="1",
                description="Item 1",
                image_url="http://url.com/img1",
                reference="ref1",
                quantity=1,
            ),
            Item(
                sku="2",
                description="Item 2",
                image_url="http://url.com/img2",
                reference="ref2",
                quantity=2,
            ),
        ]

        sobreescreve_recupera_itens_por_pedido(itens)
        resposta = client.get("/orders/7e290683-d67b-4f96-a940-44bef1f69d21/items")
        assert resposta.json() == itens

    def test_quando_fonte_de_pedidos_falha_um_erro_deve_ser_retornado(
        self, client, sobreescreve_recupera_itens_por_pedido
    ):
        sobreescreve_recupera_itens_por_pedido(FalhaDeComunicacaoError())
        resposta = client.get("/orders/ea78b59b-885d-4e7b-9cd0-d54acadb4933/items")
        assert resposta.status_code == HTTPStatus.BAD_GATEWAY


