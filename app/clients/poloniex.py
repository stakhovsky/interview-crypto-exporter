import typing

import libs.http


class CurrencyPair(typing.TypedDict):
    lowestAsk: str
    highestBid: str


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

    async def return_ticker(
        self,
    ) -> TickerResponse:
        response = await self._transport.get(
            url=self._base,
            query=dict(
                command='returnTicker',
            ),
            headers=dict(
                Accept='application/json',
            ),
        )
        return response.json
