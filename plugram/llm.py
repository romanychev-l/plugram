import asyncio
from openai import OpenAI


CORRECT_SYSTEM_PROMPT = (
    "You are an English language tutor. If the user writes Russian words or phrases "
    "in an English sentence, translate them to English. Also correct any grammar, "
    "spelling, or stylistic issues. Output ONLY the corrected text, nothing else."
)

SUMMARIZE_SYSTEM_PROMPT = (
    "You summarize Telegram chat fragments. Output a concise summary in the language "
    "of the source messages. Use 2-6 short bullet points. No preamble, no closing remarks."
)

FACT_SYSTEM_PROMPT = (
    "You analyze arguments objectively. Given a thread of messages between people, "
    "explain who is right on the merits, which arguments hold, and which are weak. "
    "Be specific and concrete. Reply in the language of the thread. No fluff."
)

TWIN_SYSTEM_TEMPLATE = (
    "Below are sample messages written by the user, separated by blank lines. "
    "Reply to the next prompt in the same style — same vocabulary, length, tone, "
    "punctuation. Stay natural. Do not use emoji unless the samples do.\n\n"
    "--- SAMPLES ---\n{samples}\n--- END SAMPLES ---"
)


class LLM:
    def __init__(self, api_key: str, model: str = "deepseek/deepseek-v3.2"):
        self._client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        self.model = model

    async def _chat(self, messages: list[dict], model: str | None = None) -> str:
        def _call():
            response = self._client.chat.completions.create(
                model=model or self.model,
                messages=messages,
            )
            return response.choices[0].message.content.strip()
        return await asyncio.to_thread(_call)

    async def correct_text(self, text: str) -> str:
        return await self._chat([
            {"role": "system", "content": CORRECT_SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ])

    async def query(self, text: str) -> str:
        return await self._chat([{"role": "user", "content": text}])

    async def summarize(self, text: str, instruction: str | None = None) -> str:
        user = text if not instruction else f"{instruction}\n\n---\n{text}"
        return await self._chat([
            {"role": "system", "content": SUMMARIZE_SYSTEM_PROMPT},
            {"role": "user", "content": user},
        ])

    async def fact_check(self, thread: str) -> str:
        return await self._chat([
            {"role": "system", "content": FACT_SYSTEM_PROMPT},
            {"role": "user", "content": thread},
        ])

    async def twin_reply(self, samples: list[str], prompt: str) -> str:
        joined = "\n\n".join(samples)
        return await self._chat([
            {"role": "system", "content": TWIN_SYSTEM_TEMPLATE.format(samples=joined)},
            {"role": "user", "content": prompt},
        ])
