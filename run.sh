#!/bin/bash

# 1. Автоматически загружаем переменные из файла .env, если он существует
if [ -f .env ]; then
    # Читаем файл, удаляем комментарии и пустые строки, затем экспортируем
    export $(grep -v '^#' .env | sed 's/ *= *.*//' | xargs)
    export $(grep -v '^#' .env | xargs)
else
    echo "Ошибка: Файл .env не найден!"
    exit 1
fi

# Имя вашей Docker-сети и тома
DOCKER_NETWORK="pizza_bot_network"
POSTGRES_VOLUME="postgres_data"
POSTGRES_CONTAINER="postgres_17"
BOT_CONTAINER="pizza_bot"
BOT_IMAGE="kirillgdeveloper/pizza_bot:latest"

# 2. Логика обработки команд (аналог таргетов в Makefile)
case "$1" in
  docker_volume)
    docker volume create "$POSTGRES_VOLUME" || true
    ;;

  docker_net)
    docker network create "$DOCKER_NETWORK" || true
    ;;

  postgres_run)
    # Сначала запускаем создание тома и сети (как зависимости в Makefile)
    docker volume create "$POSTGRES_VOLUME" || true
    docker network create "$DOCKER_NETWORK" || true
    
    # Запуск защищенной базы данных
    docker run -d \
      --name "$POSTGRES_CONTAINER" \
      -e POSTGRES_USER="$POSTGRES_USER" \
      -e POSTGRES_PASSWORD="$POSTGRES_PASSWORD" \
      -e POSTGRES_DB="$POSTGRES_DB" \
      -p "127.0.0.1:$POSTGRES_HOST_PORT:$POSTGRES_CONTAINER_PORT" \
      -v "$POSTGRES_VOLUME":/var/lib/postgresql/data \
      --health-cmd="pg_isready -U $POSTGRES_USER" \
      --health-interval=10s \
      --health-timeout=5s \
      --health-retries=5 \
      --health-start-period=30s \
      --network "$DOCKER_NETWORK" \
      postgres:17
    ;;

  postgres_stop)
    docker stop "$POSTGRES_CONTAINER" || true
    docker rm "$POSTGRES_CONTAINER" || true
    ;;

  build)
    docker build -t "$BOT_IMAGE" -f Dockerfile .
    ;;

  push)
    docker push "$BOT_IMAGE"
    ;;

  run)
    docker run -d \
      --name "$BOT_CONTAINER" \
      --restart unless-stopped \
      -e POSTGRES_HOST="$POSTGRES_CONTAINER" \
      -e POSTGRES_PORT="$POSTGRES_CONTAINER_PORT" \
      -e POSTGRES_USER="$POSTGRES_USER" \
      -e POSTGRES_PASSWORD="$POSTGRES_PASSWORD" \
      -e POSTGRES_DB="$POSTGRES_DB" \
      -e BOT_TOKEN_URI="$BOT_TOKEN_URI" \
      --network "$DOCKER_NETWORK" \
      "$BOT_IMAGE"
    ;;

  stop)
    docker stop "$BOT_CONTAINER" || true
    docker rm "$BOT_CONTAINER" || true
    ;;

  *)
    # Справка, если команда введена неверно или пустая
    echo "Использование: sh run.sh {postgres_run|postgres_stop|build|push|run|stop}"
    exit 1
    ;;
esac
