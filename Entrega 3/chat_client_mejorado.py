import pika
import json
import threading
import time

# Función para recibir mensajes en la cola de respuestas
def receive_messages():

    credentials = pika.PlainCredentials('user', 'password')
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost', credentials=credentials)
    )
    channel = connection.channel()
    
    # callback para procesarlos
    def callback(ch, method, properties, body):
        response = json.loads(body)
        print("\n--- Respuesta del chatbot ---")
        print(f"a tu pregunta: {response['question']}")
        print(f"respuesta: {response['answer']}")
        print("\nEscriba otra pregunta (o 'salir' para terminar):")

    # se declara la cola de respuestas
    channel.queue_declare(queue='answers_queue', durable=True)
    channel.basic_consume(
        queue='answers_queue',
        on_message_callback=callback,
        auto_ack=True
    )
    
    print("Esperando respuesta...")
    channel.start_consuming()

# Función para enviar preguntas a la cola de preguntas
def send_question(question):

    credentials = pika.PlainCredentials('user', 'password')
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost', credentials=credentials)
    )
    channel = connection.channel()
    
    # hay que asegurarse de que la cola de preguntas existe
    channel.queue_declare(
        queue='questions_queue',
        durable=True,
        arguments={
            'x-dead-letter-exchange': '',
            'x-dead-letter-routing-key': 'questions_queue_dlq'
        }
    )
    
    # se envía la pregunta
    channel.basic_publish(
        exchange='',
        routing_key='questions_queue',
        body=json.dumps({"question": question}),
        properties=pika.BasicProperties(delivery_mode=2)
    )
    
    connection.close()

# Se inicia el hilo para recibir mensajes
receiver_thread = threading.Thread(target=receive_messages)
receiver_thread.daemon = True
receiver_thread.start()

print("--- Cliente de chat --")
print("Preguntas disponibles para probar:")
print("- hola")
print("- horario de clases")
print("- sala de clases")
print("- que puedes hacer")
print("- nombre del profesor")
print("\nEscribe la pregunta (o 'salir' para terminar):")

try:
    while True:
        question = input("> ").strip()
        if question.lower() == 'salir':
            break
        if question:
            send_question(question)
            time.sleep(0.1) # mini pausa para evitar solapamiento de prints
except KeyboardInterrupt:
    print("\nCerrando...")

print("Hasta luego !!")