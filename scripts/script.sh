#!/bin/bash
cd "$(dirname "$0")/.." || exit

# Очистка Python кэша
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null

# Остановка и удаление контейнеров проекта
docker compose down

# Запуск
if [ "$1" = "--up" ] || [ "$1" = "-u" ]; then
    echo "🚀 Запускаем контейнеры..."
    docker compose up --build
fi