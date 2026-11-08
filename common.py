import redis

NEW_QUESTION = "Новый вопрос"
GIVE_UP = "Сдаться"
SCORE = "Мой счёт"
DEFAULT_QUESTIONS_PATH = "/opt/quiz-bot/quiz-questions"


def create_redis_client(redis_url: str) -> redis.Redis:
    return redis.from_url(
        redis_url,
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5,
    )
