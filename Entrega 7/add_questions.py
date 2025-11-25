import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

qa_pairs = {
    "hola": "Hola !!, en que puedo ayudarte?",
    "como estas": "Estoy bien !!, gracias por preguntar, en que puedo ayudarte?",
    "quien eres": "Soy un chatbot académico diseñado para ayudarte con tus preguntas :)",
    "que puedes hacer": "Puedo responder preguntas sobre diversos temas, que te gustaría saber?",
    "adios": "Hasta luego !! que tengas un buen día :D",
    "nombre del profesor": "RAFIK MAS\'\'AD NASRA",
    "sala de clases": "Sala A012, UTFSM",
    "horario de clases": "Las clases son los días lunes de 16:05 a 18:40 hrs."
}
for question, answer in qa_pairs.items():
    redis_client.set(question.lower(), answer)
    print(f"Agregado: {question} -> {answer}")

print("\nPreguntas cargadas exitosamente en Redis !!")