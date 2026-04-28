from .base import Command, Module


class AskModule(Module):
    description = "Ask the LLM. Use as `.ask <text>`, or reply to a message with `.ask` or `.ask <followup>`."
    triggers = [Command("ask", aliases=["a"])]

    async def handle(self, event, command, args) -> None:
        args = (args or "").strip()
        reply_msg = await event.message.get_reply_message() if event.message.is_reply else None

        if not args and not reply_msg:
            await event.message.reply(
                "Usage: `.ask <text>`, or reply to a message with `.ask` (optionally with a follow-up)."
            )
            return

        if reply_msg and reply_msg.text:
            if args:
                prompt = f"{args}\n\n---\n{reply_msg.text}"
            else:
                prompt = reply_msg.text
        else:
            prompt = args

        result = await self.ctx.llm.query(prompt)
        await event.message.reply(result)
