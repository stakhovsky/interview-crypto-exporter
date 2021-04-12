import typing

import app
import libs


async def export_currency_pairs(
    exmo_base: str,
    kraken_base: str,
    poloniex_base: str,
    pairs: app.entity.CurrencyPairs = (),
) -> typing.NoReturn:
    transport = libs.http.Transport()

    collector = app.repos.collector.CollectorRegistry(
        collectors=(
            app.repos.collector.ExmoCollector(
                client=app.clients.exmo.Client(
                    transport=transport,
                    base=exmo_base,
                ),
            ),
            app.repos.collector.KrakenCollector(
                client=app.clients.kraken.Client(
                    transport=transport,
                    base=kraken_base,
                ),
            ),
            app.repos.collector.PoloniexCollector(
                client=app.clients.poloniex.Client(
                    transport=transport,
                    base=poloniex_base,
                ),
            ),
        ),
    )
    exporter = app.repos.exporter.SortedStdoutExporter()

    await app.usecases.export_currency_pairs(
        collector=collector,
        exporter=exporter,
        pairs=pairs,
    )
