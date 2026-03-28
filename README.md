# 🛒 Shopping List

Веб-приложение для списка покупок. Тёмный дизайн в стиле Apple.
Список автоматически синхронизируется каждые 3 секунды.

## Функции

- ✅ Добавлять продукты (название, количество, единица измерения)
- ✅ Отмечать купленные (чекбокс)
- ✅ Менять количество (+/−)
- ✅ Редактировать название (двойной клик)
- ✅ Удалять отдельные позиции
- ✅ Очищать всё купленное одним кнопкой
- ✅ Авто-обновление каждые 3 секунды

## Локальный запуск

```bash
pip install -r requirements.txt
python app.py
# → http://localhost:5000
```

## Деплой на Railway

### 1. Создать репозиторий на GitHub

```bash
cd shopping-list
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/shopping-list.git
git push -u origin main
```

### 2. Деплой на Railway

1. Зайди на [railway.app](https://railway.app) → **New Project**
2. Выбери **Deploy from GitHub repo**
3. Выбери репозиторий `shopping-list`
4. Railway автоматически определит Python и запустит приложение
5. Зайди в **Settings → Networking → Generate Domain** — получишь публичный URL

### Переменные окружения (опционально)

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `PORT`     | Порт (Railway ставит сам) | `5000` |
| `DB_PATH`  | Путь к SQLite файлу | `shopping.db` |

> **Важно:** SQLite хранит данные в файле внутри контейнера. При каждом новом деплое Railway данные сбрасываются. Если нужно постоянное хранение — добавь PostgreSQL volume в Railway или используй Railway Volume.

## Структура

```
shopping-list/
├── app.py              # Flask backend + REST API
├── templates/
│   └── index.html      # Фронтенд (всё в одном файле)
├── requirements.txt    # Flask + Gunicorn
├── Procfile            # Команда запуска
├── railway.json        # Конфиг Railway
└── .gitignore
```

## API

| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/api/items` | Все позиции |
| POST | `/api/items` | Добавить |
| PATCH | `/api/items/:id` | Обновить (name/quantity/unit/bought) |
| DELETE | `/api/items/:id` | Удалить |
| DELETE | `/api/items/clear-bought` | Удалить все купленные |
