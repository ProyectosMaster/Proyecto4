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


def actualizar_cassandra(usuario, session):
    # Obtener movie_ids de eventos_usuario con acción "visto"

    check_user_stmt = session.prepare(
        "SELECT movie_id FROM recommendations WHERE user_id = ? LIMIT 1"
    )
    result = session.execute(check_user_stmt, (usuario,))
    if result.one():
        rows_eventos = session.execute(
            "SELECT movie_id FROM eventos_usuario WHERE user_id = %s AND accion = 'visto'",
            (usuario,),
        )
        peliculas_vistas = {row.movie_id for row in rows_eventos}

        # Solo si hay películas vistas, UPDATE
        if peliculas_vistas:
            update_seen_stmt = session.prepare(
                "UPDATE recommendations SET seen = true WHERE user_id = ? AND movie_id = ?"
            )

            for movie_id in peliculas_vistas:
                session.execute(update_seen_stmt, (usuario, movie_id))


def peliculas_vistas(usuario, session, df_peliculas):
    rows_eventos = session.execute(
        "SELECT movie_id FROM eventos_usuario WHERE user_id = %s AND accion = 'visto' ALLOW FILTERING",
        (usuario,),
    )
    peliculas_ojeadas = {row.movie_id for row in rows_eventos}

    peliculas_vistas = []
    for pelicula in peliculas_ojeadas:
        movie_row = df_peliculas[df_peliculas["id"] == int(pelicula)]
        if movie_row.empty:
            continue

        titulo = movie_row["title"].values[0]
        sinopsis = movie_row["overview"].values[0]
        img_path = movie_row["poster_path"].values[0]
        score = movie_row["vote_average"].values[0]
        rec = {
            "movieId": int(pelicula),
            "titulo": titulo,
            "sinopsis": sinopsis,
            "score": float(score),
            "img_path": img_path,
            "seen": True,
        }
        peliculas_vistas.append(rec)

    return peliculas_vistas
