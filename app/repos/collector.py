import asyncio
import itertools
import typing

from .. import (
    clients,
    constants,
    entity,
)


@typing.runtime_checkable
class Collector(typing.Protocol):
    __slots__ = tuple()

    async def collect(
        self,
        currency_pairs: entity.CurrencyPairs = (),
    ) -> typing.Sequence[entity.CurrencyPairData]:
        pass


CollectResponse = typing.TypeVar('CollectResponse')


class PairInfo(typing.TypedDict):
    ask: float
    bid: float


class BaseCollector(Collector):
    _EXCHANGE = None
    _CURRENCIES_MAP: dict = None
    _CURRENCY_PAIR_GLUE = ''

    __slots__ = tuple()

    def _get_currency_pair_code(
        self,
        currency_pair: entity.CurrencyPair,
    ) -> typing.Union[
        str,
        typing.Literal[None],
    ]:
        first_part = self._CURRENCIES_MAP.get(currency_pair[0])
        second_part = self._CURRENCIES_MAP.get(currency_pair[1])

        if not first_part or not second_part:
            return None

        return f'{first_part}{self._CURRENCY_PAIR_GLUE}{second_part}'

    def _get_currency_pair_for_code(
        self,
        currency_pair_code: str,
    ) -> typing.Union[
        entity.CurrencyPair,
        typing.Literal[None],
    ]:
        try:
            first_part, second_part = \
                currency_pair_code.split(self._CURRENCY_PAIR_GLUE, 1)
        except ValueError:
            return None

        first, second = None, None
        for key, value in self._CURRENCIES_MAP.items():
            if key == first_part:
                first = value
            if key == second_part:
                second = value
            if first is not None and second is not None:
                break

        if first is None or second is None:
            return None

        return first, second

    async def _do_collect(self) -> CollectResponse:
        raise NotImplementedError()

    def _find_pair_info(
        self,
        currency_pair_code: str,
        response: CollectResponse,
    ) -> typing.Union[
        PairInfo,
        typing.Literal[None],
    ]:
        raise NotImplementedError()

    def _get_pairs_info(
        self,
        response: CollectResponse,
    ) -> typing.Sequence[typing.Tuple[str, PairInfo]]:
        raise NotImplementedError()

    def _build_pair_data(
        self,
        currency_pair: entity.CurrencyPair,
        pair_info: PairInfo,
    ) -> entity.CurrencyPairData:
        return entity.CurrencyPairData(
            exchange=self._EXCHANGE,
            first=currency_pair[0],
            second=currency_pair[1],
            **pair_info,
        )

    def _collect_for_currency_pairs(
        self,
        response: CollectResponse,
        currency_pairs: entity.CurrencyPairs = (),
    ) -> typing.Sequence[entity.CurrencyPairData]:
        result = []

        for currency_pair in currency_pairs:
            currency_pair_code = self._get_currency_pair_code(
                currency_pair=currency_pair,
            )

            if currency_pair_code is None:
                continue

            pair_info = self._find_pair_info(
                currency_pair_code=currency_pair_code,
                response=response,
            )

            if pair_info is None:
                continue

            result.append(self._build_pair_data(
                currency_pair=currency_pair,
                pair_info=pair_info,
            ))

        return result

    def _collect_all_known(
        self,
        response: CollectResponse,
    ) -> typing.Sequence[entity.CurrencyPairData]:
        result = []

        for currency_pair_code, pair_info in self._get_pairs_info(
            response=response,
        ):
            currency_pair = self._get_currency_pair_for_code(
                currency_pair_code=currency_pair_code,
            )

            if currency_pair is None:
                continue

            pair_info = self._find_pair_info(
                currency_pair_code=currency_pair_code,
                response=response,
            )

            if pair_info is None:
                continue

            result.append(self._build_pair_data(
                currency_pair=currency_pair,
                pair_info=pair_info,
            ))

        return result

    async def collect(
        self,
        currency_pairs: entity.CurrencyPairs = (),
    ) -> typing.Sequence[entity.CurrencyPairData]:
        response = await self._do_collect()

        if currency_pairs:
            result = self._collect_for_currency_pairs(
                response=response,
                currency_pairs=currency_pairs,
            )
        else:
            result = self._collect_all_known(
                response=response,
            )

        return result


class ExmoCollector(BaseCollector):
    _EXCHANGE = constants.EXMO_EXCHANGE_NAME
    _CURRENCIES_MAP = constants.EXMO_EXCHANGE_CURRENCIES
    _CURRENCY_PAIR_GLUE = constants.EXMO_EXCHANGE_PAIR_GLUE

    __slots__ = (
        '_client',
    )

    def __init__(
        self,
        client: clients.exmo.Client,
    ):
        self._client = client

    async def _do_collect(self) -> clients.exmo.TickerResponse:
        return await self._client.get_ticker()

    def _find_pair_info(
        self,
        currency_pair_code: str,
        response: clients.exmo.TickerResponse,
    ) -> typing.Union[
        PairInfo,
        typing.Literal[None],
    ]:
        data = response.get(currency_pair_code)

        if not data:
            return None

        return PairInfo(
            ask=float(data.get('buy_price') or 0),
            bid=float(data.get('sell_price') or 0),
        )

    def _get_pairs_info(
        self,
        response: CollectResponse,
    ) -> typing.Sequence[typing.Tuple[str, PairInfo]]:
        return response.items()


class KrakenCollector(BaseCollector):
    _EXCHANGE = constants.KRAKEN_EXCHANGE_NAME
    _CURRENCIES_MAP = constants.KRAKEN_EXCHANGE_CURRENCIES
    _CURRENCY_PAIR_GLUE = constants.KRAKEN_EXCHANGE_PAIR_GLUE

    _TAG = constants.KRAKEN_EXCHANGE_PAIR_TAG

    __slots__ = (
        '_client',
    )

    def __init__(
        self,
        client: clients.kraken.Client,
    ):
        self._client = client

    async def _do_collect(self) -> clients.kraken.TickerResponse:
        return await self._client.get_tickers()

    def _find_pair_info(
        self,
        currency_pair_code: str,
        response: clients.kraken.TickerResponse,
    ) -> typing.Union[
        PairInfo,
        typing.Literal[None],
    ]:
        tickers = response.get('tickers')

        if not isinstance(tickers, list):
            return None

        for ticker in tickers:
            ticker: clients.kraken.CurrencyPair

            if not (
                ticker.get('pair') == currency_pair_code and
                ticker.get('tag') == self._TAG
            ):
                continue

            return PairInfo(
                bid=ticker.get('bid') or 0,
                ask=ticker.get('ask') or 0,
            )

        return None

    def _get_pairs_info(
        self,
        response: CollectResponse,
    ) -> typing.Sequence[typing.Tuple[str, PairInfo]]:
        result = []

        tickers = response.get('tickers')
        if not isinstance(tickers, list):
            return result

        for ticker in tickers:
            ticker: clients.kraken.CurrencyPair

            if ('pair' not in ticker) or (ticker.get('tag') != self._TAG):
                continue

            result.append((ticker.get('pair'), ticker))

        return result


class PoloniexCollector(BaseCollector):
    _EXCHANGE = constants.POLONIEX_EXCHANGE_NAME
    _CURRENCIES_MAP = constants.POLONIEX_EXCHANGE_CURRENCIES
    _CURRENCY_PAIR_GLUE = constants.POLONIEX_EXCHANGE_PAIR_GLUE

    __slots__ = (
        '_client',
    )

    def __init__(
        self,
        client: clients.poloniex.Client,
    ):
        self._client = client

    async def _do_collect(self) -> clients.poloniex.TickerResponse:
        return await self._client.return_ticker()

    def _find_pair_info(
        self,
        currency_pair_code: str,
        response: clients.poloniex.TickerResponse,
    ) -> typing.Union[
        PairInfo,
        typing.Literal[None],
    ]:
        data = response.get(currency_pair_code)

        if data is None:
            return None

        return PairInfo(
            ask=float(data.get('lowestAsk') or 0),
            bid=float(data.get('highestBid') or 0),
        )

    def _get_pairs_info(
        self,
        response: CollectResponse,
    ) -> typing.Sequence[typing.Tuple[str, PairInfo]]:
        return response.items()


class CollectorRegistry(Collector):
    __slots__ = (
        '_collectors',
    )

    def __init__(
        self,
        collectors: typing.Sequence[Collector],
    ):
        self._collectors = collectors

    async def collect(
        self,
        currency_pairs: entity.CurrencyPairs = (),
    ) -> typing.Sequence[entity.CurrencyPairData]:
        # FIXME: потенциальная утечка памяти
        results = await asyncio.gather(*(
            collector.collect(
                currency_pairs=currency_pairs,
            )
            for collector in self._collectors
        ))
        return tuple(itertools.chain.from_iterable(results))
