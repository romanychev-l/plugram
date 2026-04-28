import re
from datetime import datetime, timedelta, timezone

from ..util import format_messages
from .base import Command, Module


_DURATION_RE = re.compile(r"^(\d+)\s*([mhd])$", re.IGNORECASE)


def _parse_args(args: str) -> tuple[str, int | timedelta]:
    """Return (mode, value) where mode is 'count' or 'duration' or 'default'."""
    args = (args or "").strip()
    if not args:
        return ("default", 30)
    m = _DURATION_RE.match(args)
    if m:
        n = int(m.group(1))
        unit = m.group(2).lower()
        if unit == "m":
            return ("duration", timedelta(minutes=n))
        if unit == "h":
            return ("duration", timedelta(hours=n))
        if unit == "d":
            return ("duration", timedelta(days=n))
    if args.isdigit():
        n = max(1, min(int(args), 200))
        return ("count", n)
    return ("default", 30)


class TldrModule(Module):
    description = (
        "Summarize messages. `.tldr` on a reply summarizes that message. "
        "`.tldr 50` summarizes the last 50 messages. `.tldr 1h` / `.tldr 30m` / `.tldr 2d` for time windows."
    )
    triggers = [Command("tldr", aliases=["t"])]

    async def handle(self, event, command, args) -> None:
        args = (args or "").strip()

        if not args and event.message.is_reply:
            reply_msg = await event.message.get_reply_message()
            if reply_msg and reply_msg.text:
                summary = await self.ctx.llm.summarize(reply_msg.text)
                await event.message.reply(summary)
                return

        mode, value = _parse_args(args)
        chat = await event.get_chat()
        messages = []
        if mode == "duration":
            cutoff = datetime.now(timezone.utc) - value
            async for m in self.ctx.client.iter_messages(chat, limit=500):
                if m.id == event.message.id:
                    continue
                if m.date and m.date < cutoff:
                    break
                messages.append(m)
        else:
            limit = value if mode == "count" else 30
            async for m in self.ctx.client.iter_messages(chat, limit=limit + 1):
                if m.id == event.message.id:
                    continue
                messages.append(m)
                if len(messages) >= limit:
                    break

        if not messages:
            await event.message.reply("No messages to summarize.")
            return

        messages.reverse()
        text = format_messages(messages)
        summary = await self.ctx.llm.summarize(text)
        await event.message.reply(summary)
