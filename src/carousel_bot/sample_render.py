from pathlib import Path

from carousel_bot.openai_service import sample_carousel
from carousel_bot.renderer import render_carousel


def main() -> None:
    paths = render_carousel(sample_carousel(), Path("output/sample"))
    for path in paths:
        print(path)


if __name__ == "__main__":
    main()

