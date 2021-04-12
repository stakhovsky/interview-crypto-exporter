import typing

import libs.http


class CurrencyPair(typing.TypedDict):
    buy_price: str
    sell_price: str


TickerResponse = typing.Dict[str, CurrencyPair]


class Client:
    __slots__ = (
        '_transport',
        '_base',
    )

    def __init__(
        self,
        transport: libs.http.Transport,
        base: str,
    ):
        self._transport = transport
        self._base = base

    async def get_ticker(
        self,
    ) -> TickerResponse:
        response = await self._transport.get(
            url=libs.http.join(
                pieces=(
                    self._base,
                    'ticker',
                ),
            ),
        )
        return response.json
