import BotonAuth from '../components/BotonAuth';
import { useState, useEffect } from "react";
import axios from "axios";

const Pelis = () => {
  type Pelicula = {
    movieId: number;
    titulo: string;
    sinopsis: string;
    score: number;
    img_path: string;
  };

  const [recomendaciones, setRecomendaciones] = useState<Pelicula[]>([]);
  const [loading, setLoading] = useState(false);

  const obtenerRecomendaciones = async () => {
    try {
      const res = await axios.get("http://localhost:5000/api/pelis");
      setRecomendaciones(res.data);
    } catch (error) {
      console.error("Error al obtener recomendaciones", error);
      setRecomendaciones([]);
    } finally {
      setLoading(false);
    }
  };

  // 👇 Aquí es donde usas useEffect
  useEffect(() => {
    setLoading(true);
    obtenerRecomendaciones();
  }, []);

  return (
    <div>
      {loading && (
        <div style={{ marginTop: "1rem" }}>
          <span className="spinner" style={{ fontSize: "1rem" }}>
            ⏳
          </span>{" "}
          Buscando recomendaciones...
        </div>
      )}
      <h1>Página protegida de Pelis 🎬</h1>
      <ul>
        {recomendaciones.map((peli, i) => (
          <li key={i}>
            <h3>{peli.titulo}</h3>
            <p>{peli.sinopsis}</p>
            <p>Puntuación: {peli.score.toFixed(2)}</p>
            <img
              src={`/${peli.img_path}`}
              alt={peli.titulo}
              style={{ width: "200px" }}
            />
          </li>
        ))}
      </ul>

      <BotonAuth />
    </div>
  );
};

export default Pelis;
