import random
from functools import partial

import vk_api
from dotenv import load_dotenv
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkEventType, VkLongPoll

from common import (
    GIVE_UP,
    NEW_QUESTION,
    SCORE,
    create_redis_client,
    get_env,
    get_optional_env,
    get_questions_path,
    load_questions,
)
from quiz_utils import clean_answer, normalize_answer


def get_keyboard():
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button(NEW_QUESTION, color=VkKeyboardColor.PRIMARY)
    keyboard.add_button(GIVE_UP, color=VkKeyboardColor.NEGATIVE)
    keyboard.add_line()
    keyboard.add_button(SCORE, color=VkKeyboardColor.SECONDARY)
    return keyboard.get_keyboard()


def send_message(vk, user_id, text):
    vk.messages.send(
        user_id=user_id,
        message=text,
        random_id=random.randint(1, 2**31 - 1),
        keyboard=get_keyboard(),
    )


def handle_new_question_request(vk, redis_client, questions, user_id):
    user_key = f"vk-{user_id}"

    question = random.choice(questions)
    redis_client.set(user_key, question)
    send_message(vk, user_id, question)


def handle_give_up(vk, redis_client, questions, questions_answers, user_id):
    user_key = f"vk-{user_id}"
    question = redis_client.get(user_key)

    if not question:
        send_message(vk, user_id, "Сначала нажмите «Новый вопрос».")
        return

    correct_answer = questions_answers.get(question)
    if correct_answer:
        send_message(vk, user_id, f"Правильный ответ: {correct_answer}")
    else:
        send_message(vk, user_id, "Вопрос не найден. Нажмите «Новый вопрос».")

    new_question = random.choice(questions)
    redis_client.set(user_key, new_question)
    send_message(vk, user_id, new_question)


def handle_score(vk, user_id):
    send_message(vk, user_id, "Счёт пока не реализован.")


def handle_solution_attempt(vk, redis_client, questions_answers, user_id, user_message):
    user_key = f"vk-{user_id}"
    question = redis_client.get(user_key)

    if not question:
        send_message(vk, user_id, "Нажмите «Новый вопрос».")
        return

    correct_answer = questions_answers.get(question)
    if not correct_answer:
        send_message(vk, user_id, "Вопрос не найден. Нажмите «Новый вопрос».")
        return

    cleaned_correct_answer = clean_answer(correct_answer)
    user_answer = normalize_answer(user_message)

    if user_answer and user_answer in cleaned_correct_answer:
        redis_client.delete(user_key)
        send_message(
            vk,
            user_id,
            "Правильно! Поздравляю! Нажмите «Новый вопрос».",
        )
        return

    send_message(vk, user_id, "Неправильно… Попробуешь ещё раз?")


def main():
    load_dotenv()

    vk_token = get_env("VK_BOT_TOKEN")
    redis_url = get_env("REDIS_URL")
    questions_path = get_questions_path()
    group_id = get_optional_env("VK_GROUP_ID")

    redis_client = create_redis_client(redis_url)
    redis_client.ping()

    questions_answers, questions = load_questions(questions_path)

    vk_session = vk_api.VkApi(token=vk_token)
    vk = vk_session.get_api()
    if group_id:
        longpoll = VkLongPoll(vk_session, group_id=int(group_id))
    else:
        longpoll = VkLongPoll(vk_session)

    new_question_handler = partial(
        handle_new_question_request,
        vk,
        redis_client,
        questions,
    )
    give_up_handler = partial(
        handle_give_up,
        vk,
        redis_client,
        questions,
        questions_answers,
    )
    score_handler = partial(handle_score, vk)
    solution_attempt_handler = partial(
        handle_solution_attempt,
        vk,
        redis_client,
        questions_answers,
    )

    for event in longpoll.listen():
        if event.type != VkEventType.MESSAGE_NEW or not event.to_me:
            continue

        user_id = event.user_id
        user_message = (event.text or "").strip()
        if not user_message:
            continue

        if user_message == NEW_QUESTION:
            new_question_handler(user_id)
            continue

        if user_message == GIVE_UP:
            give_up_handler(user_id)
            continue

        if user_message == SCORE:
            score_handler(user_id)
            continue

        solution_attempt_handler(user_id, user_message)


if __name__ == "__main__":
    main()
