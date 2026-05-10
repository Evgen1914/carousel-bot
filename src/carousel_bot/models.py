from pydantic import BaseModel, ConfigDict, Field


class Slide(BaseModel):
    model_config = ConfigDict(extra="forbid")

    eyebrow: str = Field(description="Short label above the main title")
    title: str = Field(description="Slide headline")
    body: str = Field(description="Slide body text, 1-3 short sentences")


class CarouselPost(BaseModel):
    model_config = ConfigDict(extra="forbid")

    topic: str
    audience: str
    tone: str
    slides: list[Slide] = Field(min_length=5, max_length=9)
    caption: str
    hashtags: list[str] = Field(min_length=5, max_length=14)
    safety_note: str
