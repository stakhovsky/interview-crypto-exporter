import dataclasses
import typing

from .. import (
    entity,
)


@typing.runtime_checkable
class Exporter(typing.Protocol):
    async def export(
        self,
        currency_pairs: typing.Sequence[entity.CurrencyPairData],
    ) -> typing.NoReturn:
        pass


class SortedStdoutExporter(Exporter):
    _TITLE = ('Currency Pair', 'Exchange', 'Ask', 'Bid')
    _TITLE_PATTERN = '{:15s} | {:10s} | {:14s} | {:14s}'
    _PATTERN = (
        '{first:7s} {second:7s} | {exchange:10s} | {ask:14.4f} | {bid:14.4f}'
    )

    async def export(
        self,
        currency_pairs: typing.Sequence[entity.CurrencyPairData],
    ) -> typing.NoReturn:
        print(self._TITLE_PATTERN.format(*self._TITLE))
        for pair in sorted(
            currency_pairs,
            key=lambda p: (p.first, p.second, p.ask, p.bid),
        ):
            print(self._PATTERN.format(**dataclasses.asdict(pair)))
