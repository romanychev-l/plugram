from .ask import AskModule
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
    "manage": ManageModule,
}
