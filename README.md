# Instagram Carousel Bot

Telegram-бот для подготовки образовательных каруселей Instagram в нише гинекологии.

Бот принимает тему поста, генерирует структуру карусели, caption и хэштеги, затем рендерит готовые PNG-слайды 1080x1350.

## Быстрый старт

```bash
cd /Users/evgenijskokov/instagram-carousel-bot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
cp .env.example .env
```

Заполните `.env`:

```env
TELEGRAM_BOT_TOKEN=...
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-5.4-mini
```

Проверить генерацию слайдов без Telegram и OpenAI:

```bash
carousel-sample
```

Запуск бота:

```bash
carousel-bot
```

## Как пользоваться

В Telegram отправьте боту тему, например:

```text
Мифы о болезненных месячных
```

Или подробнее:

```text
Тема: подготовка к приему у гинеколога
ЦА: женщины 25-40
Тон: спокойный, заботливый, экспертный
Слайдов: 7
```

## Важно

Контент задуман как образовательный. Бот не должен выдавать диагнозы, схемы лечения, дозировки препаратов или заменять консультацию врача.
