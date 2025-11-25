import pytest
import json
from unittest.mock import MagicMock
from chat_bot_service import ChatbotConsumer


@pytest.fixture
def mock_redis():
    """Crea un cliente Redis falso."""
    return MagicMock()

@pytest.fixture
def mock_channel():
    """Crea un canal RabbitMQ falso."""
    return MagicMock()

@pytest.fixture
def consumer(mock_redis, mock_channel):
    """
    Instancia el consumidor inyectándole el Redis falso.
    Esto evita que intente conectarse a la base de datos real.
    """
    chatbot = ChatbotConsumer(redis_client=mock_redis)
    chatbot.channel = mock_channel 
    return chatbot

@pytest.fixture
def mock_method():
    """Simula los metadatos del mensaje de RabbitMQ."""
    method = MagicMock()
    method.delivery_tag = 123 
    return method


def test_get_answer_found(consumer, mock_redis):
    mock_redis.get.return_value = "Arquitectura de software"
    
    respuesta = consumer.get_answer("Nombre de la asignatura")
    
    assert respuesta == "Arquitectura de software"
    mock_redis.get.assert_called_with("nombre de la asignatura")

def test_get_answer_not_found(consumer, mock_redis):
    mock_redis.get.return_value = None
    
    respuesta = consumer.get_answer("Pregunta inexistente")
    
    assert "Lo siento" in respuesta


def test_callback_success_flow(consumer, mock_redis, mock_channel, mock_method):
    """Prueba el flujo completo: Recibe -> Consulta Redis -> Responde -> ACK"""
    
    mock_redis.get.return_value = "Respuesta OK"
    body_entrante = json.dumps({"question": "hola"}).encode('utf-8')
    mock_props = MagicMock()

    consumer._callback(mock_channel, mock_method, mock_props, body_entrante)

    expected_response = json.dumps({"question": "hola", "answer": "Respuesta OK"})
    
    mock_channel.basic_publish.assert_called_once()
    args, kwargs = mock_channel.basic_publish.call_args
    assert kwargs['body'] == expected_response
    assert kwargs['routing_key'] == 'answers_queue'
    
    mock_channel.basic_ack.assert_called_once_with(delivery_tag=123)


def test_callback_malformed_json(consumer, mock_channel, mock_method):
    """Prueba de error: JSON corrupto -> NACK (sin reencolar) -> DLQ"""
    
    body_entrante = b"{ esto no es json }"
    mock_props = MagicMock()

    consumer._callback(mock_channel, mock_method, mock_props, body_entrante)

    mock_channel.basic_publish.assert_not_called()
    mock_channel.basic_nack.assert_called_once_with(delivery_tag=123, requeue=False)


def test_callback_missing_question_field(consumer, mock_channel, mock_method):
    """
    Escenario 3: JSON válido pero falta la clave 'question'.
    """
    body = json.dumps({"clave_incorrecta": "valor"}).encode('utf-8')
    mock_props = MagicMock()

    consumer._callback(mock_channel, mock_method, mock_props, body)

    mock_channel.basic_nack.assert_called_once_with(
        delivery_tag=mock_method.delivery_tag, 
        requeue=False
    )