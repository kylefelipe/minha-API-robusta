from http import HTTPStatus
from uuid import UUID

from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse

from api_pedidos.excecao import FalhaDeComunicacaoError, PedidoNaoEncontradoError
from api_pedidos.magalu_api import recuperar_itens_por_pedido
from api_pedidos.schema import ErrorResponse, HealthCheckResponse, Item

app = FastAPI()


# def recuperar_itens_por_pedido(order_id: UUID) -> list[Item]:
#     pass


@app.exception_handler(PedidoNaoEncontradoError)
def tratar_erro_pedido_nao_encontrado(request: Request, exc: PedidoNaoEncontradoError):
    return JSONResponse(
        status_code=HTTPStatus.NOT_FOUND,
        content={"message": "Pedido não encontrado"},
    )


@app.exception_handler(FalhaDeComunicacaoError)
def trata_erro_falha_de_comunicacao(request: Request, exc: FalhaDeComunicacaoError):
    return JSONResponse(
        status_code=HTTPStatus.BAD_GATEWAY,
        content={"message": "Falha de comunicação"},
    )


@app.get(
    "/healthcheck",
    tags=["healthcheck"],
    summary="Integridade do sistema",
    description="Checa se o servidor está online",
    response_model=HealthCheckResponse,
)
async def healthcheck():
    return HealthCheckResponse(status="ok")


@app.get(
    "/orders/{order_id}/items",
    responses={
        HTTPStatus.NOT_FOUND.value: {
            "description": "Pedido não encontrado",
            "model": ErrorResponse,
        },
        HTTPStatus.BAD_GATEWAY.value: {
            "description": "Falha de comunicação com servidor remoto",
            "model": ErrorResponse,
        },
    },
    tags=["orders"],
    summary="Itens de um pedido",
    description="Retorna todos os itens de um determinado pedido",
    response_model=list[Item],
)
def list_items(items: list[Item] = Depends(recuperar_itens_por_pedido)):
    return items
