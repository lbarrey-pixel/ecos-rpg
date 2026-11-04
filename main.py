import logging

from dotenv import load_dotenv

from ecos_rpg.bot.app import criar_aplicacao

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


def main() -> None:
    load_dotenv()
    print("🌑 Ecos do Fim — bot iniciado.")
    criar_aplicacao().run_polling()


if __name__ == "__main__":
    main()
