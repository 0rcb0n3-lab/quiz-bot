import random
from enum import Enum
from functools import partial

from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup
from telegram.ext import (
    CommandHandler,
    ConversationHandler,
    Filters,
    MessageHandler,
    Updater,
)

from common import (
    GIVE_UP,
    NEW_QUESTION,
    SCORE,
    create_redis_client,
    get_env,
    get_questions_path,
    load_questions,
)
from quiz_utils import clean_answer, normalize_answer


class BotStates(Enum):
    QUIZ = 1


def get_keyboard():
    keyboard = [
        [NEW_QUESTION, GIVE_UP],
        [SCORE],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def start(update, context):
    update.message.reply_text(
        "Привет! Я бот для викторин!",
        reply_markup=get_keyboard(),
    )


def handle_new_question_request(redis_client, questions, update, context):
    user_key = f"tg-{update.message.chat_id}"

    question = random.choice(questions)
    redis_client.set(user_key, question)

    update.message.reply_text(question)
    return BotStates.QUIZ


def handle_solution_attempt(redis_client, questions_answers, update, context):
    user_key = f"tg-{update.message.chat_id}"
    question = redis_client.get(user_key)

    if not question:
        update.message.reply_text("Сначала нажмите «Новый вопрос».")
        return ConversationHandler.END

    correct_answer = questions_answers.get(question)
    if not correct_answer:
        update.message.reply_text("Вопрос не найден. Нажмите «Новый вопрос».")
        return ConversationHandler.END

    user_answer = normalize_answer(update.message.text)
    cleaned_correct_answer = clean_answer(correct_answer)

    if user_answer and user_answer in cleaned_correct_answer:
        redis_client.delete(user_key)
        update.message.reply_text(
            "Правильно! Поздравляю! Для следующего вопроса нажмите «Новый вопрос»."
        )
        return ConversationHandler.END

    update.message.reply_text("Неправильно… Попробуешь ещё раз?")
    return BotStates.QUIZ


def handle_give_up(redis_client, questions, questions_answers, update, context):
    user_key = f"tg-{update.message.chat_id}"
    question = redis_client.get(user_key)

    if not question:
        update.message.reply_text("Сначала нажмите «Новый вопрос».")
        return ConversationHandler.END

    correct_answer = questions_answers.get(question)
    if correct_answer:
        update.message.reply_text(f"Правильный ответ: {correct_answer}")
    else:
        update.message.reply_text("Вопрос не найден. Нажмите «Новый вопрос».")

    new_question = random.choice(questions)
    redis_client.set(user_key, new_question)
    update.message.reply_text(new_question)

    return BotStates.QUIZ


def handle_score(update, context):
    update.message.reply_text("Счёт пока не реализован.")
    return BotStates.QUIZ


def main():
    load_dotenv()

    tg_token = get_env("TG_BOT_TOKEN")
    redis_url = get_env("REDIS_URL")
    questions_path = get_questions_path()

    redis_client = create_redis_client(redis_url)
    redis_client.ping()

    questions_answers, questions = load_questions(questions_path)

    new_question_handler = partial(
        handle_new_question_request,
        redis_client,
        questions,
    )
    solution_attempt_handler = partial(
        handle_solution_attempt,
        redis_client,
        questions_answers,
    )
    give_up_handler = partial(
        handle_give_up,
        redis_client,
        questions,
        questions_answers,
    )

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            MessageHandler(Filters.regex(f"^{NEW_QUESTION}$"), new_question_handler),
        ],
        states={
            BotStates.QUIZ: [
                MessageHandler(
                    Filters.regex(f"^{NEW_QUESTION}$"), new_question_handler
                ),
                MessageHandler(Filters.regex(f"^{GIVE_UP}$"), give_up_handler),
                MessageHandler(Filters.regex(f"^{SCORE}$"), handle_score),
                MessageHandler(
                    Filters.text & ~Filters.command, solution_attempt_handler
                ),
            ],
        },
        fallbacks=[
            CommandHandler("start", start),
        ],
    )

    updater = Updater(tg_token, use_context=True)
    updater.dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
