import asyncio
import json
import logging
from pathlib import Path

from .base import Command, Module, Passive


log = logging.getLogger(__name__)

MIN_LIVE_LEN = 30


class TwinModule(Module):
    description = (
        "Reply in your own writing style. `.twin <text>` or reply to a message with `.twin`. "
        "Subcommands: `.twin stats`, `.twin import @channel`, `.twin import /path/to/result.json`. "
        "Also passively collects your outgoing messages into a corpus."
    )
    triggers = [Command("twin"), Passive()]

    async def handle(self, event, command, args) -> bool | None:
        if command == "twin":
            await self._command(event, args or "")
            return None
        # Passive: store live message in corpus, never block other passives.
        text = (event.message.text or "").strip()
        if (
            text
            and not text.startswith(".")
            and len(text) >= MIN_LIVE_LEN
        ):
            try:
                self.ctx.corpus.add(text, source="live")
            except Exception:
                log.exception("Failed to store live message in corpus")
        return False

    async def _command(self, event, args: str) -> None:
        args = args.strip()
        if args == "stats":
            stats = self.ctx.corpus.stats()
            parts = [f"{k}: {v}" for k, v in stats["by_source"].items()]
            await event.message.reply(
                f"Corpus: {stats['total']} messages" + (f" ({', '.join(parts)})" if parts else "")
            )
            return

        if args.startswith("import"):
            target = args[len("import"):].strip()
            if not target:
                await event.message.reply("Usage: `.twin import @channel` or `.twin import /path/to/result.json`")
                return
            asyncio.create_task(self._import(event, target))
            return

        reply_msg = await event.message.get_reply_message() if event.message.is_reply else None
        if not args and not reply_msg:
            await event.message.reply(
                "Usage: `.twin <text>` or reply to a message with `.twin`."
            )
            return

        prompt = args if args else (reply_msg.text or "")
        if not prompt:
            await event.message.reply("Nothing to reply to.")
            return

        samples = self.ctx.corpus.sample(n=30)
        if not samples:
            await event.message.reply(
                "Corpus is empty. Send some messages first, or use `.twin import @channel`."
            )
            return

        result = await self.ctx.llm.twin_reply(samples, prompt)
        if reply_msg:
            await reply_msg.reply(result)
        else:
            await event.message.reply(result)

    async def _import(self, event, target: str) -> None:
        try:
            if target.startswith("/") or target.endswith(".json"):
                count = await self._import_export_file(target)
                await event.message.reply(f"Imported {count} messages from {target}.")
                return
            count = await self._import_channel(target)
            await event.message.reply(f"Imported {count} messages from {target}.")
        except Exception as e:
            log.exception("Import failed")
            await event.message.reply(f"Import failed: {e}")

    async def _import_channel(self, channel: str) -> int:
        texts: list[str] = []
        async for m in self.ctx.client.iter_messages(channel):
            text = (m.text or "").strip()
            if text and len(text) >= MIN_LIVE_LEN:
                texts.append(text)
        return self.ctx.corpus.add_many(texts, source="channel_import")

    async def _import_export_file(self, path: str) -> int:
        p = Path(path).expanduser()
        with p.open("r", encoding="utf-8") as f:
            data = json.load(f)
        texts: list[str] = []
        messages = data.get("messages") if isinstance(data, dict) else data
        own_id = None
        if isinstance(data, dict):
            own_id = data.get("personal_information", {}).get("user_id")
        for m in messages or []:
            if not isinstance(m, dict):
                continue
            if own_id is not None and m.get("from_id") not in {f"user{own_id}", own_id}:
                continue
            text = m.get("text")
            if isinstance(text, list):
                text = "".join(
                    seg if isinstance(seg, str) else seg.get("text", "")
                    for seg in text
                )
            if not isinstance(text, str):
                continue
            text = text.strip()
            if text and len(text) >= MIN_LIVE_LEN:
                texts.append(text)
        return self.ctx.corpus.add_many(texts, source="export_import")
