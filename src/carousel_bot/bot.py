from __future__ import annotations

import asyncio
import socket
from datetime import datetime
from pathlib import Path

from aiogram import Bot, Dispatcher, F
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.filters import CommandStart
from aiogram.types import BufferedInputFile, Message

from carousel_bot.config import get_settings
from carousel_bot.openai_service import CarouselGenerator
from carousel_bot.renderer import render_carousel


OUTPUT_ROOT = Path("output")


def _caption_text(caption: str, hashtags: list[str], safety_note: str) -> str:
    tags = " ".join(hashtags)
    parts = [caption]
    if safety_note.strip():
        parts.append(safety_note)
    parts.append(tags)
    return "\n\n".join(parts)


async def start(message: Message) -> None:
    await message.answer(
        "Пришлите тему карусели для Instagram.\n\n"
        "Например: «Мифы о болезненных месячных» или подробный бриф с ЦА, тоном и количеством слайдов."
    )


async def generate_carousel(message: Message) -> None:
    if not message.text:
        await message.answer("Пришлите текстовый бриф: тему, ЦА, тон и желаемое количество слайдов.")
        return

    status = await message.answer("Готовлю сценарий и слайды. Обычно это занимает 30-90 секунд.")
    try:
        generator = CarouselGenerator()
        post = await asyncio.to_thread(generator.generate, message.text)
        run_dir = OUTPUT_ROOT / datetime.now().strftime("%Y%m%d_%H%M%S")
        paths = await asyncio.to_thread(render_carousel, post, run_dir)

        await status.edit_text("Слайды готовы. Отправляю карусель.")
        for path in paths:
            data = path.read_bytes()
            await message.answer_photo(BufferedInputFile(data, filename=path.name))

        await message.answer(_caption_text(post.caption, post.hashtags, post.safety_note))
    except Exception as exc:
        await status.edit_text(
            "Не получилось сгенерировать карусель. Проверьте TELEGRAM_BOT_TOKEN, OPENAI_API_KEY и попробуйте еще раз.\n\n"
            f"Техническая причина: {type(exc).__name__}: {exc}"
        )


async def main() -> None:
    settings = get_settings()
    if not settings.telegram_bot_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")

    session = AiohttpSession(proxy=settings.telegram_proxy or None)
    # Some servers prefer broken IPv6 routes for api.telegram.org. Keep Telegram
    # traffic on IPv4 unless a proxy is configured.
    if not settings.telegram_proxy:
        session._connector_init["family"] = socket.AF_INET

    bot = Bot(token=settings.telegram_bot_token, session=session)
    dp = Dispatcher()
    dp.message.register(start, CommandStart())
    dp.message.register(generate_carousel, F.text)

    while True:
        try:
            await dp.start_polling(bot)
        except Exception as exc:
            print(f"Polling failed: {type(exc).__name__}: {exc}. Retrying in 20 seconds.", flush=True)
            await asyncio.sleep(20)


if __name__ == "__main__":
    asyncio.run(main())


def run() -> None:
    asyncio.run(main())
