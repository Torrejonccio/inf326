    - Renato Ramírez   | ROL: 202173639-5
    - Matias Torrejon  | ROL: 202173543-7

# Chatbot Académico - Microservicio

Este proyecto implementa un microservicio de chatbot académico que responde preguntas frecuentes usando Redis y RabbitMQ. Todo el sistema se ejecuta a traves de Docker Compose.

En esta versión del microservicio, puesto que como aún no se han hecho las conexiones con los demas microservicios, lo que se hizo fue crear un script que se encarga de agregar preguntas junto con sus respuestas, de manera que se pueden agregar o modificar preguntas y respuestas con este script, ademas se creo otro programa que se encarga de probar el Chat-bot, dando una pequeña interfaz para poder hacer las preguntas (solo las preguntas que se agregaron con el script anterior). Para la base de conocimineto se utilizó *Redis* y para la comunicación por colas se usó *RabbitMQ*.

## Instrucciones de uso

### 1. Requisitos
- Docker y Docker Compose instalados
- Python 3.10+ (para los scripts)

### 2. Levantar el sistema
sh
docker-compose up --build

Esto inicia Redis, RabbitMQ y el servicio del chatbot.

### 3. Cargar preguntas y respuestas
Editar add_questions.py para añadir preguntas con sus respectivas respuestas. Ejecutando el siguiente comando:
sh
python add_questions.py


### 4. Probar el chatbot
Para ejecutar el cliente interactivo:
sh
python chat_client_mejorado.py

## Archivos principales
- chat-bot_service.py: Servicio principal del chatbot.
- add_questions.py: Script para cargar preguntas/respuestas en Redis.
- chat_client_mejorado.py: Cliente interactivo para probar el chatbot.
- docker-compose.yml y Dockerfile: Configuración para Docker.
