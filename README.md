# Проект чат на FastAPI

## Стек технологий

- **FastAPI**: Веб-фреймворк для создания API.
- **SQLAlchemy**: ORM для работы с базой данных.
- **Alembic**: Инструмент для управления миграциями базы данных.
- **PostgreSQL**: Реляционная база данных.
- **Docker**: Платформа для контейнеризации приложений.
- **Docker Compose**: Инструмент для определения и запуска многоконтейнерных Docker приложений.
- **dotenv**: Библиотека для загрузки переменных окружения из файла `.env`.

## Установка и запуск

### Предварительные требования

- Docker
- Docker Compose

### Шаги для запуска

1. Клонируйте репозиторий:

    ```sh
    git clone https://github.com/eromanv/websocket-chat.git
    cd websocket-chat
    ```

2. Создайте файл `.env` и добавьте в него следующие переменные окружения:

    ```ini
    DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/chat
    POSTGRES_DB=chat
    POSTGRES_USER=user
    POSTGRES_PASSWORD=password
    ```

3. Запустите Docker Compose:

    ```sh
    docker-compose up --build
    ```

4. Приложение будет доступно по адресу `http://localhost:8000`.

### Миграции базы данных

Для применения миграций базы данных используйте Alembic:

```sh
docker-compose exec app alembic upgrade head
```

## Примеры использования

### Веб-сокеты

Для подключения к чату используйте следующий WebSocket URL:

```
ws://localhost:8000/ws/{chat_id}/{user_id}
```

#### Проверка WebSocket на Ubuntu

Для проверки WebSocket соединения на Ubuntu можно использовать утилиту `websocat`. Установите её с помощью следующей команды:

```sh
sudo snap install websocat
```

Затем подключитесь к WebSocket серверу:

```sh
websocat ws://localhost:8000/ws/{chat_id}/{user_id}
```

### Получение истории чата

Для получения истории сообщений используйте следующий HTTP GET запрос:

```http
GET /history/{chat_id}?limit=10&offset=0
```

Пример:

```sh
curl -X GET "http://localhost:8000/history/1?limit=10&offset=0"
```

### Инициализация базы данных

Для инициализации базы данных с тестовыми данными выполните:

```sh
docker-compose exec app python init_db.py
```

### Проверка содержимого базы данных

Для проверки содержимого базы данных выполните:

```sh
docker-compose exec app python check_db.py
```

## Заключение

Этот проект демонстрирует создание простого чата с использованием FastAPI, SQLAlchemy и WebSocket. Docker и Docker Compose используются для упрощения развертывания и управления зависимостями.
