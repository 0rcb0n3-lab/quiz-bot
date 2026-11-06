# Quiz Bot

Telegram и VK боты для викторины.

Бот задаёт пользователю случайный вопрос и проверяет правильность ответа.
Если ответ правильный — бот поздравляет пользователя.
Если неправильный — предлагает попробовать ещё раз.

Текущий вопрос пользователя хранится в Redis.

---

## Ссылки на ботов

- Telegram: https://t.me/YOUR_TELEGRAM_BOT
- VK: https://vk.com/YOUR_GROUP

---

## Возможности

- команда `/start`;
- кнопка «Новый вопрос»;
- кнопка «Сдаться» с показом правильного ответа;
- кнопка «Мой счёт» (пока заглушка);
- проверка ответа без учёта регистра, `ё/е`, пунктуации и лишних пробелов;
- удаление текущего вопроса из Redis после правильного ответа.

---

## Как это работает

Вопросы читаются из `.txt` файлов в папке `quiz-questions/`.
Файлы должны быть в кодировке `KOI8-R`.

Формат файла:

```text
Вопрос 1:
Текст вопроса?

Ответ:
Текст ответа.
```

Папка `quiz-questions/` не входит в репозиторий — её нужно добавить отдельно.

---

## Структура проекта

```text
common.py       — общие настройки, Redis и загрузка вопросов
quiz_utils.py   — парсинг вопросов и нормализация ответов
tgbot.py        — Telegram бот
vkbot.py        — VK бот
```

---

## Как запустить локально

### 1. Клонировать репозиторий

```bash
git clone https://github.com/0rcb0n3-lab/quiz-bot.git
cd quiz-bot
```

### 2. Установить зависимости

Нужны Python `3.10+` и [uv](https://docs.astral.sh/uv/).

```bash
uv sync
```

### 3. Создать файл `.env`

```bash
cp .env.example .env
```

Заполнить переменные:

```env
TG_BOT_TOKEN=your_telegram_token
VK_BOT_TOKEN=your_vk_token
VK_GROUP_ID=your_vk_group_id
REDIS_URL=redis://:password@127.0.0.1:6379/0
QUESTIONS_PATH=./quiz-questions
```

`VK_GROUP_ID` нужен только для VK-сообщества.
`QUESTIONS_PATH` для локального запуска указывает на локальную папку с вопросами.

### 4. Запустить Redis

```bash
redis-server --bind 127.0.0.1 --port 6379 --requirepass password
```

Пароль в `REDIS_URL` должен совпадать с паролем Redis.

### 5. Запустить ботов

Telegram:

```bash
uv run python tgbot.py
```

VK:

```bash
uv run python vkbot.py
```

---

## Проверка

```bash
uv run pytest -q
uv run ruff check .
```

---

## Запуск на сервере

Скопировать проект в `/opt/quiz-bot`, положить `.env` и папку `quiz-questions/`, затем установить зависимости:

```bash
cd /opt/quiz-bot
uv sync --python 3.10
```

Перезапустить VK-бота:

```bash
systemctl restart quiz-vkbot.service
systemctl status quiz-vkbot.service
```

Если Telegram-сервис настроен:

```bash
systemctl restart quiz-tgbot.service
```

---

Не коммитьте `.env` и папку `quiz-questions/` — они содержат секреты и большие данные.
