import logging
from typing import TYPE_CHECKING

from .modules import REGISTRY
from .modules.base import Command, Passive

if TYPE_CHECKING:
    from .modules.base import Module


log = logging.getLogger(__name__)


class Dispatcher:
    def __init__(self, ctx):
        self.ctx = ctx
        self.modules: dict[str, "Module"] = {}
        self.reload()

    def reload(self) -> None:
        self.modules = {}
        for name, cls in REGISTRY.items():
            if self.ctx.config.is_enabled(name):
                instance = cls(self.ctx)
                instance.name = name
                self.modules[name] = instance
        log.info("Loaded modules: %s", ", ".join(self.modules) or "(none)")

    async def dispatch(self, event) -> None:
        text = event.message.text or ""
        if not text:
            return

        if text.startswith("."):
            await self._dispatch_command(event, text)
            return

        await self._dispatch_passive(event, text)

    async def _dispatch_command(self, event, text: str) -> None:
        body = text[1:]
        if not body or body[0].isspace():
            return
        parts = body.split(maxsplit=1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        for module in self.modules.values():
            for trigger in module.triggers:
                if not isinstance(trigger, Command):
                    continue
                if cmd == trigger.name or cmd in trigger.aliases:
                    try:
                        await module.handle(event, cmd, args)
                    except Exception:
                        log.exception("Module %s failed on .%s", module.name, cmd)
                    return

    async def _dispatch_passive(self, event, text: str) -> None:
        for module in self.modules.values():
            for trigger in module.triggers:
                if not isinstance(trigger, Passive):
                    continue
                try:
                    handled = await module.handle(event, None, text)
                except Exception:
                    log.exception("Passive module %s failed", module.name)
                    handled = False
                if handled:
                    return
