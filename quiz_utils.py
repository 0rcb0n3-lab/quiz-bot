import os
import re
from pathlib import Path

QUESTIONS_DIR = Path(__file__).resolve().parent / "quiz-questions"
ENCODING = "koi8-r"

_QUESTION_RE = re.compile(r"^Вопрос\s+\d+\s*:\s*(.*)$")
_ANSWER_RE = re.compile(r"^Ответ\s*:\s*(.*)$")
_NON_WORD_RE = re.compile(r"[^\w\s]")
_SPACES_RE = re.compile(r"\s+")


def load_questions_from_file(file_path: str | os.PathLike[str]) -> dict[str, str]:
    """Загружает вопросы и ответы из одного файла в словарь."""
    with open(file_path, encoding=ENCODING, errors="replace") as file:
        content = file.read()

    blocks = content.replace("\r\n", "\n").split("\n\n")
    questions_answers: dict[str, str] = {}
    question: str | None = None

    for block in blocks:
        first_line = block.split("\n", 1)[0].strip()

        if _QUESTION_RE.match(first_line):
            question = block.split(":", 1)[1].strip()

        elif _ANSWER_RE.match(first_line) and question:
            answer = block.split(":", 1)[1].strip()
            if answer:
                questions_answers[question] = answer

    return questions_answers


def load_questions_from_directory(
    directory_path: str | os.PathLike[str] = QUESTIONS_DIR,
) -> dict[str, str]:
    """Собирает вопросы и ответы из всех .txt файлов папки."""
    all_questions_answers: dict[str, str] = {}

    for filename in sorted(os.listdir(directory_path)):
        if not filename.endswith(".txt"):
            continue

        file_path = os.path.join(directory_path, filename)
        all_questions_answers.update(load_questions_from_file(file_path))

    return all_questions_answers


def normalize_answer(answer: str) -> str:
    """Приводит текст к виду, удобному для сравнения."""
    answer = answer.lower().replace("ё", "е")
    answer = _NON_WORD_RE.sub(" ", answer)
    return _SPACES_RE.sub(" ", answer).strip()


def clean_answer(answer: str) -> str:
    """Готовит ответ к сравнению: убирает уточнения и нормализует текст."""
    answer = answer.split(".")[0]
    answer = answer.split("(")[0]
    return normalize_answer(answer)
