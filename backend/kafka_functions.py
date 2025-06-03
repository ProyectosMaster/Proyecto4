from kafka import KafkaConsumer
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable
from datetime import datetime
import json
import time


def producer():
    for i in range(10):

        try:
            producer = KafkaProducer(
                bootstrap_servers="kafka:9092",
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            )
        except NoBrokersAvailable:
            print(f"[Kafka] No broker available. Retrying ({i+1}/10)...")
            time.sleep(8)

    return producer


def consumer(session):

    consumer = KafkaConsumer(
        "eventos_peliculas",
        bootstrap_servers=["kafka:9092"],
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id="cassandra-consumer-group",
    )

    for mensaje in consumer:
        evento = mensaje.value
        try:
            user_id = int(evento["usuario"])
            movie_id = int(evento["pelicula_id"])
            accion = evento["accion"]

            timestamp_str = evento["timestamp"]
            try:
                timestamp = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S.%f")
            except ValueError:
                timestamp = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S")

            query = """
            INSERT INTO eventos_usuario (user_id, movie_id, accion, timestamp)
            VALUES (%s, %s, %s, %s)
            """
            session.execute(query, (user_id, movie_id, accion, timestamp))
            print(f"Evento insertado: {evento}")
        except Exception as e:
            print(f"Error al procesar evento: {evento} -> {e}")
