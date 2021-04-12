import asyncio
import typing

import fire

import app
import config
import script


async def _export_currency_pairs(
    pairs: app.entity.CurrencyPairs = (),
) -> typing.NoReturn:
    await script.export_currency_pairs(
        exmo_base=config.EXMO_BASE,
        kraken_base=config.KRAKEN_BASE,
        poloniex_base=config.POLONIEX_BASE,
        pairs=pairs,
    )


def export_currency_pairs(
    pairs: str = '',
) -> typing.NoReturn:
    """
    Получить статистику покупки/продажи на разных биржах.
    Анализируемые пары задаются опциональным аргументом pairs в формате
    "x1:x2,x3:x4,...".
    """
    pairs = [
        pair
        for pair in (p.split(':', 2) for p in pairs.split(','))
        if (
            len(pair) == 2 and
            pair[0] in app.constants.CURRENCIES and
            pair[1] in app.constants.CURRENCIES
        )
    ]

    asyncio.run(_export_currency_pairs(
        pairs=pairs,
    ))


if __name__ == '__main__':
    fire.Fire(dict(
        export_currency_pairs=export_currency_pairs,
    ))
