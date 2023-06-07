import os
from http import HTTPStatus
from uuid import UUID

import httpx

from api_pedidos.excecao import (
    FalhaDeComunicacaoError,
    PedidoNaoEncontradoError,
)
from api_pedidos.schema import Item

# tenant e apikey fixos para facilitar o desenvolvimento
APIKEY = os.environ.get("APIKEY", "5734143a-595d-405d-9c97-6c198537108f")
TENANT_ID = os.environ.get("TENANT_ID", "21fea73c-e244-497a-8540-be0d3c583596")
# MAGALU_API_URL = "https://alpha.api.magalu.com"
MAGALU_API_URL = "http://127.0.0.1:8080"
MAESTRO_SERVICE_URL = f"{MAGALU_API_URL}/maestro/v1"


def _recupera_itens_por_pacote(uuid_do_pedido: UUID, uuid_do_pacote: UUID):
    response = httpx.get(
        (
            f"{MAESTRO_SERVICE_URL}/orders/"
            f"{uuid_do_pedido}/packages/{uuid_do_pacote}/items"
        ),
        headers={"X-Api-Key": APIKEY, "X-Tenant-Id": TENANT_ID},
    )
    response.raise_for_status()
    return [
        Item(
            sku=item["product"]["code"],
            description=item["product"].get("description", ""),
            image_url=item["product"].get("image_url", ""),
            reference=item["product"].get("reference", ""),
            quantity=item["quantity"],
        )
        for item in response.json()
    ]


def recuperar_itens_por_pedido(order_id: UUID) -> list[Item]:
    try:
        response = httpx.get(
            f"{MAESTRO_SERVICE_URL}/orders/{order_id}",
            headers={"X-Api-Key": APIKEY, "X-Tenant-Id": TENANT_ID},
        )
        response.raise_for_status()
        pacotes = response.json()["packages"]
        print(">>>: ", pacotes[0])
        itens = []
        for pacote in pacotes:
            itens.extend(_recupera_itens_por_pacote(order_id, pacote["uuid"]))
        return itens
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == HTTPStatus.NOT_FOUND:
            raise PedidoNaoEncontradoError() from exc
        raise exc
    except httpx.RequestError as exc:
        raise FalhaDeComunicacaoError() from exc
