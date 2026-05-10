import json

from openai import OpenAI

from carousel_bot.config import get_settings
from carousel_bot.models import CarouselPost
from carousel_bot.prompts import SYSTEM_PROMPT, user_prompt


def _carousel_json_schema() -> dict:
    return CarouselPost.model_json_schema()


class CarouselGenerator:
    def __init__(self) -> None:
        settings = get_settings()
        self.model = settings.openai_model
        self.client = OpenAI(api_key=settings.openai_api_key)

    def generate(self, brief: str) -> CarouselPost:
        response = self.client.responses.create(
            model=self.model,
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt(brief)},
            ],
            text={
                "format": {
                    "type": "json_schema",
                    "name": "gynecology_carousel_post",
                    "schema": _carousel_json_schema(),
                    "strict": True,
                }
            },
        )
        return CarouselPost.model_validate_json(response.output_text)


def sample_carousel() -> CarouselPost:
    raw = {
        "topic": "Мифы о болезненных месячных",
        "audience": "Женщины 25-45, которые хотят лучше понимать свое здоровье",
        "tone": "Спокойный, заботливый, доказательный",
        "slides": [
            {
                "eyebrow": "Женское здоровье",
                "title": "Боль во время месячных: где миф, а где сигнал?",
                "body": "Дискомфорт бывает у многих. Но сильная боль, которая выбивает из жизни, не должна считаться нормой.",
            },
            {
                "eyebrow": "Миф 1",
                "title": "«Нужно просто потерпеть»",
                "body": "Терпеть боль месяц за месяцем не обязательно. Важно обсудить симптомы с врачом и понять возможные причины.",
            },
            {
                "eyebrow": "Миф 2",
                "title": "«После родов все пройдет»",
                "body": "Так бывает не всегда. Откладывать консультацию из-за этого мифа не стоит.",
            },
            {
                "eyebrow": "На что смотреть",
                "title": "Когда стоит записаться к врачу",
                "body": "Если боль усилилась, появились необычные выделения, слабость, температура или цикл резко изменился.",
            },
            {
                "eyebrow": "Подготовка",
                "title": "Что рассказать на приеме",
                "body": "Когда начинается боль, сколько длится, что помогает, насколько она мешает обычным делам.",
            },
            {
                "eyebrow": "Бережно к себе",
                "title": "Ваши ощущения важны",
                "body": "Даже если раньше говорили «у всех так», вы имеете право разобраться и получить поддержку.",
            },
            {
                "eyebrow": "CTA",
                "title": "Сохраните пост",
                "body": "И покажите врачу список симптомов на приеме. Так разговор будет спокойнее и точнее.",
            },
        ],
        "caption": "Болезненные месячные часто обесценивают, но сильная боль — повод внимательнее отнестись к себе. Сохраните чек-лист и обсудите симптомы со специалистом.",
        "hashtags": ["#гинеколог", "#женскоездоровье", "#месячные", "#цикл", "#здоровье", "#гинекология"],
        "safety_note": "Пост носит образовательный характер и не заменяет консультацию врача.",
    }
    return CarouselPost.model_validate(raw)

