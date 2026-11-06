import os

import redis

from quiz_utils import load_questions_from_directory

NEW_QUESTION = "Новый вопрос"
GIVE_UP = "Сдаться"
SCORE = "Мой счёт"
DEFAULT_QUESTIONS_PATH = "/opt/quiz-bot/quiz-questions"


def get_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Не задана переменная окружения {name}")
    return value


def get_optional_env(name: str) -> str | None:
    return os.getenv(name) or None


def get_questions_path() -> str:
    return os.getenv("QUESTIONS_PATH", DEFAULT_QUESTIONS_PATH)


def create_redis_client(redis_url: str) -> redis.Redis:
    return redis.from_url(
        redis_url,
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5,
    )


def load_questions(path: str) -> tuple[dict[str, str], list[str]]:
    questions_answers = load_questions_from_directory(path)
    if not questions_answers:
        raise RuntimeError(f"Не найдены вопросы в {path}")
    return questions_answers, list(questions_answers)
