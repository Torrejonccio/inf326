# Chatbot Académico - Microservicio

**Integrantes:**

  - Renato Ramírez   | ROL: 202173639-5
  - Matias Torrejon  | ROL: 202173543-7

-----

Este proyecto implementa un microservicio de **Chatbot Académico** diseñado para responder preguntas frecuentes sobre la asignatura (ej. "Arquitectura de Software") de manera automatizada.

El sistema utiliza:

  - **Redis:** Como base de conocimiento en memoria (clave-valor) para búsquedas rápidas.
  - **RabbitMQ:** Para la gestión asíncrona de mensajes mediante colas (`questions_queue` y `answers_queue`).
  - **Python 3.11:** Lenguaje base del servicio.

La arquitectura está totalmente contenerizada y orquestada a través de **Docker Compose**.

## Estructura del Proyecto

Los archivos principales del sistema son:

  - **`chat_bot_service.py`**: Lógica principal. Contiene la clase `ChatbotConsumer` que orquesta la conexión a RabbitMQ y las consultas a Redis.
  - **`test_chatbot.py`**: Suite de pruebas automatizada con **pytest**. Utiliza `unittest.mock` para simular Redis y RabbitMQ, permitiendo pruebas rápidas sin infraestructura real.
  - **`add_questions.py`**: Script utilitario para cargar preguntas y respuestas iniciales en Redis.
  - **`chat_client_mejorado.py`**: Cliente interactivo de terminal para simular el envío de preguntas y recepción de respuestas.
  - **`Makefile`**: Automatización de comandos para compilación, ejecución y pruebas.
  - **`docker-compose.yml`**: Configuración de infraestructura (Chatbot, Redis, RabbitMQ).

## Instrucciones de Uso

### 1\. Requisitos Previos

  - Docker Desktop (corriendo).
  - Make (opcional, recomendado para facilitar comandos).

### 2\. Despliegue del Sistema

Para construir la imagen y levantar todos los servicios (Redis, RabbitMQ y Chatbot) en segundo plano:

```bash
make all
```

*(Alternativa manual: `docker-compose up --build -d`)*

### 3\. Ejecución de Pruebas (Testing)

El proyecto cuenta con una suite de **5 pruebas** que validan la robustez del servicio. Estas pruebas se ejecutan dentro del contenedor para asegurar la consistencia del entorno y utilizan **Mocks** para aislar la lógica.

Para correr las pruebas:

```bash
make test
```

**Cobertura de Pruebas:**

1.  **`test_get_answer_found`**: Verifica que si la pregunta existe en Redis (normalizando mayúsculas/minúsculas), se retorna la respuesta correcta.
2.  **`test_get_answer_not_found`**: Verifica que si la pregunta no existe, se retorna el mensaje por defecto.
3.  **`test_callback_success_flow`**: Simula el ciclo completo de RabbitMQ: Recibir mensaje -\> Consultar Redis -\> Publicar respuesta -\> Enviar ACK.
4.  **`test_callback_malformed_json`**: Verifica que si llega un JSON corrupto (bytes inválidos), el servicio envía un NACK (sin reencolar) a la DLQ.
5.  **`test_callback_missing_question_field`**: Verifica que si el JSON es válido pero le faltan datos obligatorios (clave `question`), se maneja el error correctamente.

### 4\. Pruebas Funcionales Manuales

Si desea interactuar manualmente con el bot funcionando con los servicios reales:

**Paso A: Cargar la base de conocimiento**
Edite `add_questions.py` si desea agregar nuevas preguntas y ejecute:

```bash
python add_questions.py
```

**Paso B: Interactuar con el Chatbot**
Inicie el cliente de terminal para enviar preguntas a la cola y esperar respuestas:

```bash
python chat_client_mejorado.py
```

### 5\. Comandos del Makefile

| Comando | Descripción |
| :--- | :--- |
| `make all` | Construye la imagen y levanta el entorno completo. |
| `make test` | Ejecuta `pytest` con logs activados dentro del contenedor. |
| `make logs` | Muestra los logs del contenedor del chatbot en tiempo real. |
| `make down` | Detiene los servicios. |
| `make clean` | Detiene y elimina contenedores y volúmenes (limpieza total). |
