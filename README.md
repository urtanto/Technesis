![Лого](logo.jpg)

## Описание бота @technesis_test_xlsx_bot

Проект **Technesis** — это простой Telegram-бот на базе aiogram, который:

1. Принимает Excel-файлы (`.xlsx`) с колонками:

- **title** — название товара
- **url** — ссылка на сайт-источник
- **xpath** — путь к элементу с ценой

2. Сохраняет данные из файла в локальную базу данных **SQLite**.
3. С помощью Playwright (undetected_playwright) получает цену с переданных в Excel ссылок по указанным XPath. (
   Обход капчи не гарантирую, но в большинстве случаев работает)
4. Выводит результаты пользователю в чате и отображает статистику (количество товаров, успешные запросы, максимальную,
   минимальную и среднюю цену).

## Структура проекта

По скриншоту в репозитории можно увидеть основные файлы и директории:

- [`database/`](./database/) - моудль базы данных.
  - [`__init__.py`](./database/__init__.py) — инициализация модуля базы данных.
  - [`models`](./database/models) — модели для ORM.
    - [`products.py`](./database/models/products.py) — таблица из задания.
- [`database.db`](./database.db) — локальная база данных SQLite.
- [`.gitignore`](./.gitignore) — список исключений для Git.
- [`Dockerfile`](./Dockerfile) — Docker-образ.
- [`requirements.txt`](./requirements.txt) — зависимости.
- [`test1.xlsx`](./test1.xlsx) и [`test2.xlsx`](./test2.xlsx) — примеры Excel-файлов для загрузки боту.
- [`tg_bot.py`](./tg_bot.py) — основной код бота.

## Сборка и запуск проекта в Docker (не будет работать получение цен)

1. Собрать Docker-образ:
   ```bash
   docker build -t technesis .
   ```
2. Запустить контейнер:
   ```bash
   docker run -d technesis
   ```

3. Для остановки и удаления контейнера:
   ```bash
   docker stop container_id
   ```
   ```bash
   docker rm container_id
   ```

4. Полная очистка Docker:

   Чтобы полностью очистить все контейнеры, образы и прочие данные, используйте:
    ```bash
    docker system prune -af
    ```

   > **Внимание**: команда безвозвратно удаляет **все** контейнеры, образы, тома и кэш, не используемые в данный момент.

Ниже приведён пример README-файла, который шаг за шагом объясняет, как создать виртуальное окружение, активировать его и
запустить Python-проект с настройкой Playwright.

# Запуск бота локально

1. Создание виртуального окружения

   Перейдите в корневую директорию вашего проекта и выполните команду для создания виртуального окружения:
    ```bash
    python -m venv venv
    ```

2. Активация виртуального окружения
    ```bash
    source venv/bin/activate
    ```

3. Обновление pip
    ```bash
    pip install --upgrade pip
    ```

4. Установка зависимостей

    ```bash
    pip install -r requirements.txt
    ```

5. Настройка Playwright

   После установки пакета Playwright необходимо установить браузеры, которые он использует. Для этого выполните:
    ```bash
    playwright install chromium
    ```

6. Разрешение на запуск браузера

    ```bash
    chmod -R a+x {{path to project}}/lib/{{python version}}/site-packages/undetected_playwright/driver
    ```

7. Запуск проекта

    ```bash
    python tg_bot.py
    ```