import os
from pathlib import Path

QUESTIONS_DIR = Path(__file__).resolve().parent / "quiz-questions"
ENCODING = "koi8-r"


def load_questions_from_file(file_path: str) -> dict[str, str]:
    """Загружает вопросы и ответы из одного файла в словарь."""
    with open(file_path, "r", encoding=ENCODING, errors="replace") as file:
        content = file.read()

    blocks = content.replace("\r\n", "\n").split("\n\n")
    questions_answers = {}
    question = None

    for block in blocks:
        if block.startswith("Вопрос") and ":" in block:
            question = block.split(":", 1)[1].strip()

        elif block.startswith("Ответ") and ":" in block and question:
            answer = block.split(":", 1)[1].strip()
            if answer:
                questions_answers[question] = answer

    return questions_answers


def load_questions_from_directory(directory_path: str = QUESTIONS_DIR) -> dict[str, str]:
    """Собирает вопросы и ответы из всех .txt файлов папки."""
    all_questions_answers = {}

    for filename in sorted(os.listdir(directory_path)):
        if not filename.endswith(".txt"):
            continue

        file_path = os.path.join(directory_path, filename)
        all_questions_answers.update(load_questions_from_file(file_path))

    return all_questions_answers


def clean_answer(answer: str) -> str:
    """Готовит ответ к сравнению: убирает уточнения и приводит к нижнему регистру."""
    answer = answer.split(".")[0]
    answer = answer.split("(")[0]
    return answer.strip().lower()
