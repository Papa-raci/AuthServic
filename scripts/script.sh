!/bin/bash
set -e  # остановка при ошибках

cd "$(dirname "$0")/.." || exit 1

show_help() {
  echo "🧰  Использование: $0 [-u] [-t] [-c] [-h]"
  echo "  -u   🚀 Запустить контейнеры (docker compose up --build -d)"
  echo "  -t   🧪 Запустить тесты (pytest внутри api)"
  echo "  -c   🧹 Очистить кэш и остановить контейнеры"
  echo "  -h   📖 Показать справку"
  exit 0
}

while getopts "utch" opt; do
  case $opt in
    u)
      echo "🚀 Запускаем контейнеры..."
      docker compose up --build -d
      ;;
    t)
      echo "🧪 Запускаем тесты..."
      if ! docker compose ps | grep -q "api"; then
        echo "⚠️  Контейнер api не запущен, поднимаем..."
        docker compose up -d api
      fi
      docker compose exec api pytest
      ;;
    c)
      echo "🧹 Очищаем Python кэш..."
      find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
      find . -name "*.pyc" -delete 2>/dev/null
      echo "🧱 Останавливаем контейнеры..."
      docker compose down
      ;;
    h|*)
      show_help
      ;;
  esac
done

# если ничего не передано — показать помощь
[ $OPTIND -eq 1 ] && show_help