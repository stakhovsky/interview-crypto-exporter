import typing

import libs.http


class CurrencyPair(typing.TypedDict):
    tag: str
    pair: str
    bid: float
    ask: float


class TickerResponse(typing.TypedDict):
    result: str
    tickers: typing.Sequence[CurrencyPair]


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

    async def get_tickers(
        self,
    ) -> TickerResponse:
        response = await self._transport.get(
            url=libs.http.join(
                pieces=(
                    self._base,
                    'tickers',
                ),
            ),
        )
        return response.json
