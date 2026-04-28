from ..language import should_correct
from .base import Module, Passive


class TranslateModule(Module):
    description = "Auto-fix outgoing messages that start in English (or mix English/Russian)."
    triggers = [Passive()]

    async def handle(self, event, command, args) -> bool:
        text = event.message.text
        if not text or not should_correct(text):
            return False
        corrected = await self.ctx.llm.correct_text(text)
        if corrected and corrected != text:
            await event.message.edit(corrected)
        return True
