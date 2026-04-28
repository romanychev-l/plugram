from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class Command:
    name: str
    aliases: list[str] = field(default_factory=list)


@dataclass
class Passive:
    pass


class Module(ABC):
    name: str = ""
    description: str = ""
    triggers: list = []

    def __init__(self, ctx):
        self.ctx = ctx

    @abstractmethod
    async def handle(self, event, command: str | None, args: str) -> bool | None:
        """Return True if a passive handler consumed the message."""
