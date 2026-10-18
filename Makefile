#
# Docker commands
#

DOCKER_NETWORK=pizza_bot_network
POSTGRES_VOLUME=postgres_data
POSTGRES_CONTAINER=postgres_17
BOT_CONTAINER=pizza_bot
BOT_IMAGE=kirillgdeveloper/pizza_bot:latest

# Автоматически загружаем переменные из .env
include .env
export $(shell sed 's/=.*//' .env)

docker_volume:
	docker volume create $(POSTGRES_VOLUME) || true

docker_net:
	docker network create $(DOCKER_NETWORK) || true

postgres_run: docker_volume
	docker network create $(DOCKER_NETWORK) || true
	docker run -d \
		--name $(POSTGRES_CONTAINER) \
		--restart always \
		-e POSTGRES_USER="$(POSTGRES_USER)" \
		-e POSTGRES_PASSWORD="$(POSTGRES_PASSWORD)" \
		-e POSTGRES_DB="$(POSTGRES_DB)" \
		-p "127.0.0.1:$(POSTGRES_HOST_PORT):$(POSTGRES_CONTAINER_PORT)" \
		-v $(POSTGRES_VOLUME):/var/lib/postgresql/data \
		--health-cmd="pg_isready -U $(POSTGRES_USER)" \
		--health-interval=10s \
		--health-timeout=5s \
		--health-retries=5 \
		--health-start-period=30s \
		--network $(DOCKER_NETWORK) \
		postgres:17

postgres_stop:
	docker stop $(POSTGRES_CONTAINER) || true
	docker rm $(POSTGRES_CONTAINER) || true

run:
	docker run -d \
		--name $(BOT_CONTAINER) \
		--restart unless-stopped \
		-e POSTGRES_HOST="$(POSTGRES_CONTAINER)" \
		-e POSTGRES_PORT="$(POSTGRES_CONTAINER_PORT)" \
		-e POSTGRES_USER="$(POSTGRES_USER)" \
		-e POSTGRES_PASSWORD="$(POSTGRES_PASSWORD)" \
		-e POSTGRES_DB="$(POSTGRES_DB)" \
		-e BOT_TOKEN="$(BOT_TOKEN)" \
		--network $(DOCKER_NETWORK) \
		$(BOT_IMAGE)

stop:
	docker stop $(BOT_CONTAINER) || true
	docker rm $(BOT_CONTAINER) || true
