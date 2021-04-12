import typing

from . import (
    entity,
    repos,
)


async def export_currency_pairs(
    collector: repos.collector.Collector,
    exporter: repos.exporter.Exporter,
    pairs: entity.CurrencyPairs = (),
) -> typing.NoReturn:
    await exporter.export(
        currency_pairs=await collector.collect(
            currency_pairs=pairs,
        ),
    )
