import pika
import json
import time
import os
import logging
import signal
import redis

# Configuración
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'user')
RABBITMQ_PASS = os.getenv('RABBITMQ_PASS', 'password')
REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
QUEUE_QUESTIONS = os.getenv('QUEUE_QUESTIONS', 'questions_queue')
QUEUE_ANSWERS = os.getenv('QUEUE_ANSWERS', 'answers_queue')
QUEUE_QUESTIONS_DLQ = f"{QUEUE_QUESTIONS}_dlq"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ChatbotConsumer:
    def __init__(self, redis_client=None):
        """
        Permite inyectar un cliente de Redis. 
        Si redis_client es None, intentará conectar al real.
        """
        self.connection = None
        self.channel = None
        
        if redis_client:
            self.redis_client = redis_client
        else:
            self._connect_redis()

    def _connect_redis(self):
        try:
            self.redis_client = redis.Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)
            self.redis_client.ping()
            logging.info(f"Conectado exitosamente a Redis en {REDIS_HOST}")
        except redis.exceptions.ConnectionError as e:
            logging.error(f"No se pudo conectar a Redis: {e}")
            raise e

    def get_answer(self, question: str) -> str:
        """Busca una respuesta en Redis usando el cliente de la instancia."""
        question_lower = question.lower().strip()
        answer = self.redis_client.get(question_lower)
        if answer:
            return answer
        return "Lo siento, no tengo una respuesta para esa pregunta. Intenta ser más específico."

    def _connect_rabbitmq(self):
        # Lógica de conexión RabbitMQ
        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials)
        )
        self.channel = self.connection.channel()
        logging.info("Conectado exitosamente a RabbitMQ.")
        
        # Declaración de colas
        self.channel.queue_declare(queue=QUEUE_QUESTIONS_DLQ, durable=True)
        self.channel.queue_declare(
            queue=QUEUE_QUESTIONS,
            durable=True,
            arguments={
                'x-dead-letter-exchange': '',
                'x-dead-letter-routing-key': QUEUE_QUESTIONS_DLQ
            }
        )
        self.channel.queue_declare(queue=QUEUE_ANSWERS, durable=True)
        self.channel.basic_qos(prefetch_count=1)

    def _callback(self, ch, method, properties, body):
        try:
            message = json.loads(body)
            question = message.get("question")
            logging.info(f"Pregunta recibida: {question}")

            if not question:
                raise ValueError("El mensaje no contiene la clave 'question'")

            # Llamamos al método interno
            answer = self.get_answer(question)
            
            response_message = json.dumps({"question": question, "answer": answer})
            ch.basic_publish(
                exchange='',
                routing_key=QUEUE_ANSWERS,
                body=response_message,
                properties=pika.BasicProperties(delivery_mode=2)
            )
            logging.info(f"Respuesta enviada: {answer}")
            ch.basic_ack(delivery_tag=method.delivery_tag)

        except (json.JSONDecodeError, ValueError) as e:
            logging.error(f"Mensaje inválido: {body}. Enviando a DLQ. Error: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        except Exception as e:
            logging.error(f"Error inesperado: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    def start(self):
        while True:
            try:
                self._connect_rabbitmq()
                self.channel.basic_consume(queue=QUEUE_QUESTIONS, on_message_callback=self._callback)
                logging.info('Chatbot iniciado. Esperando preguntas...')
                self.channel.start_consuming()
            except pika.exceptions.AMQPConnectionError:
                logging.warning("Fallo conexión RabbitMQ. Reintentando en 5s...")
                time.sleep(5)
            except Exception as e:
                logging.error(f"Error crítico en consumidor: {e}. Reiniciando en 5s...")
                self.stop()
                time.sleep(5)

    def stop(self):
        if self.channel and self.channel.is_open:
            self.channel.close()
        if self.connection and self.connection.is_open:
            self.connection.close()
        logging.info("Conexión RabbitMQ cerrada.")

def main():
    try:
        consumer = ChatbotConsumer()
        
        def graceful_shutdown(signum, frame):
            logging.info("Apagando...")
            consumer.stop()
            exit(0)

        signal.signal(signal.SIGINT, graceful_shutdown)
        signal.signal(signal.SIGTERM, graceful_shutdown)

        consumer.start()
    except Exception as e:
        logging.error(f"No se pudo iniciar el servicio: {e}")
        exit(1)

if __name__ == '__main__':
    main()