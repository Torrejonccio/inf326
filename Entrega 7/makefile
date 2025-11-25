SERVICE_NAME = chatbot_service

.PHONY: all build up down test logs clean

all: build up

build:
	@echo "Construyendo la imagen..."
	docker-compose build

up:
	@echo "Levantando servicios en segundo plano..."
	docker-compose up -d

down:
	@echo "Deteniendo servicios..."
	docker-compose down

test:
	@echo "Ejecutando pruebas dentro del contenedor..."
	docker-compose exec chatbot_service pytest -v -o log_cli=true --log-cli-level=INFO

logs:
	docker-compose logs -f $(SERVICE_NAME)

clean:
	@echo "Limpiando contenedores y volúmenes..."
	docker-compose down -v
	@echo "Limpieza completada."