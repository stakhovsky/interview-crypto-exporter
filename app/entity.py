import dataclasses
import typing


CurrencyPair = typing.Tuple[str, str]
CurrencyPairs = typing.Sequence[CurrencyPair]


@dataclasses.dataclass(frozen=True)
class CurrencyPairData:
    exchange: str
    first: str
    second: str
    ask: float
    bid: float
