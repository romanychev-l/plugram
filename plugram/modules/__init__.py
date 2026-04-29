from .ask import AskModule
from .dump import DumpModule
from .fact import FactModule
from .manage import ManageModule
from .tldr import TldrModule
from .translate import TranslateModule
from .twin import TwinModule


REGISTRY: dict[str, type] = {
    "translate": TranslateModule,
    "ask": AskModule,
    "tldr": TldrModule,
    "fact": FactModule,
    "twin": TwinModule,
    "dump": DumpModule,
    "manage": ManageModule,
}
