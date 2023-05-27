from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from http import HTTPStatus
from uuid import UUID

from api_pedidos.excecao import PedidoNaoEncontradoError, FalhaDeComunicacaoError
from api_pedidos.schema import Item

app = FastAPI()


def recupera_itens_por_pedido(order_id: UUID) -> list[Item]:
    pass


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


@app.get("/healthcheck")
async def healthcheck():
    return {"status": "ok"}


@app.get("/orders/{order_id}/items")
def list_items(items: list[Item] = Depends(recupera_itens_por_pedido)):
    return items
