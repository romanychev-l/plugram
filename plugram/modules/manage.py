from .base import Command, Module


def _registry() -> dict:
    from . import REGISTRY  # lazy: avoids circular import with __init__.py
    return REGISTRY


class ManageModule(Module):
    description = (
        "Manage modules and LLM. `.mod` lists modules, `.mod on/off <name>` toggles them, "
        "`.model [<openrouter-path>]` shows or changes the LLM, `.help [name]` shows help."
    )
    triggers = [Command("mod"), Command("help"), Command("model")]

    async def handle(self, event, command, args) -> None:
        args = (args or "").strip()

        if command == "help":
            await self._help(event, args)
            return

        if command == "model":
            await self._model(event, args)
            return

        parts = args.split(maxsplit=1)
        sub = parts[0].lower() if parts else ""
        rest = parts[1] if len(parts) > 1 else ""

        if not sub or sub == "list":
            await self._list(event)
            return
        if sub == "on":
            await self._toggle(event, rest, True)
            return
        if sub == "off":
            await self._toggle(event, rest, False)
            return
        if sub == "help":
            await self._help(event, rest)
            return
        await event.message.edit("Usage: `.mod`, `.mod on <name>`, `.mod off <name>`, `.mod help [name]`")

    async def _list(self, event) -> None:
        lines = ["**Modules:**"]
        for name, cls in _registry().items():
            mark = "[on] " if self.ctx.config.is_enabled(name) else "[off]"
            desc = (cls.description or "").splitlines()[0] if cls.description else ""
            lines.append(f"`{mark}` `{name}` — {desc}")
        await event.message.edit("\n".join(lines))

    async def _toggle(self, event, name: str, enabled: bool) -> None:
        name = name.strip().lower()
        if name not in _registry():
            await event.message.edit(f"Unknown module: `{name}`")
            return
        if name == "manage":
            await event.message.edit("Refusing to toggle `manage` — you'd lock yourself out.")
            return
        self.ctx.config.set_enabled(name, enabled)
        if self.ctx.dispatcher is not None:
            self.ctx.dispatcher.reload()
        state = "enabled" if enabled else "disabled"
        await event.message.edit(f"`{name}` {state}.")

    async def _model(self, event, args: str) -> None:
        name = args.strip()
        if not name:
            await event.message.edit(f"Current model: `{self.ctx.llm.model}`")
            return
        if "/" not in name or any(c.isspace() for c in name):
            await event.message.edit(
                "Expected an OpenRouter path like `vendor/model-name`, "
                "e.g. `google/gemini-3-flash-preview`. "
                "Browse models at https://openrouter.ai/models."
            )
            return
        self.ctx.llm.model = name
        self.ctx.config.set_model(name)
        await event.message.edit(f"Model set to `{name}`.")

    async def _help(self, event, name: str) -> None:
        name = name.strip().lower()
        if name and name in _registry():
            cls = _registry()[name]
            await event.message.edit(f"**{name}**\n{cls.description}")
            return
        lines = ["**Plugram help — `.help <module>` for detail.**", ""]
        for n, cls in _registry().items():
            mark = "[on] " if self.ctx.config.is_enabled(n) else "[off]"
            lines.append(f"`{mark}` `{n}` — {(cls.description or '').splitlines()[0]}")
        lines.append("")
        lines.append(
            "Toggle: `.mod on <name>` / `.mod off <name>`. "
            "LLM: `.model [vendor/name]`. Commands use the `.` prefix."
        )
        await event.message.edit("\n".join(lines))
