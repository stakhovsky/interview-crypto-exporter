import envparse


envparse.env.read_envfile()


EXMO_BASE = envparse.env.str(
    var='EXMO_BASE',
    default='https://api.exmo.com/v1.1/',
)
KRAKEN_BASE = envparse.env.str(
    var='KRAKEN_BASE',
    default='https://futures.kraken.com/derivatives/api/v3/',
)
POLONIEX_BASE = envparse.env.str(
    var='POLONIEX_BASE',
    default='https://poloniex.com/public',
)
