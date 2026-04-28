from ..util import format_messages, walk_reply_chain
from .base import Command, Module


class FactModule(Module):
    description = "Reply with `.fact` to a message in an argument thread for an objective breakdown of who's right."
    triggers = [Command("fact")]

    async def handle(self, event, command, args) -> None:
        if not event.message.is_reply:
            await event.message.reply("Reply to a message in the argument with `.fact`.")
            return

        target = await event.message.get_reply_message()
        if target is None:
            await event.message.reply("Couldn't fetch the replied-to message.")
            return

        chain = await walk_reply_chain(target, max_depth=10)

        if len(chain) < 2:
            chat = await event.get_chat()
            siblings = []
            async for m in self.ctx.client.iter_messages(
                chat, limit=10, offset_id=target.id, reverse=False
            ):
                if m.id != event.message.id:
                    siblings.append(m)
            siblings.reverse()
            chain = siblings + [target]

        senders = {getattr(m, "sender_id", None) for m in chain if getattr(m, "sender_id", None)}
        if len(senders) < 2:
            await event.message.reply("Only one person in this thread — nothing to arbitrate.")
            return

        thread_text = format_messages(chain)
        verdict = await self.ctx.llm.fact_check(thread_text)
        await target.reply(verdict)
