import collections


EXMO_EXCHANGE_NAME = 'Exmo'
KRAKEN_EXCHANGE_NAME = 'Kraken'
POLONIEX_EXCHANGE_NAME = 'Poloniex'

CURRENCIES = collections.namedtuple(
    'Currencies',
    (
        'USD',
        'BTC',
        'ETH',
        'BCH',
        'DASH',
        'DOGE',
    )
)(
    USD='USD',
    BTC='BTC',
    ETH='ETH',
    BCH='BCH',
    DASH='DASH',
    DOGE='DOGE',
)

EXMO_EXCHANGE_CURRENCIES = {
    CURRENCIES.USD: 'USD',
    CURRENCIES.BTC: 'BTC',
    CURRENCIES.ETH: 'ETH',
    CURRENCIES.BCH: 'BCH',
    CURRENCIES.DASH: 'DASH',
    CURRENCIES.DOGE: 'DOGE',
}
KRAKEN_EXCHANGE_CURRENCIES = {
    CURRENCIES.USD: 'USD',
    CURRENCIES.BTC: 'BTC',
    CURRENCIES.ETH: 'ETH',
    CURRENCIES.BCH: 'BCH',
    CURRENCIES.DASH: 'DASH',
    CURRENCIES.DOGE: 'DOGE',
}
POLONIEX_EXCHANGE_CURRENCIES = {
    CURRENCIES.USD: 'TUSD',
    CURRENCIES.BTC: 'BTC',
    CURRENCIES.ETH: 'ETH',
    CURRENCIES.BCH: 'BCH',
    CURRENCIES.DASH: 'DASH',
    CURRENCIES.DOGE: 'DOGE',
}

EXMO_EXCHANGE_PAIR_GLUE = '_'
KRAKEN_EXCHANGE_PAIR_GLUE = ':'
POLONIEX_EXCHANGE_PAIR_GLUE = '_'

KRAKEN_EXCHANGE_PAIR_TAG = 'perpetual'