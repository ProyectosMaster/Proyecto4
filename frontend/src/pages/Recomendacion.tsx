import { useState } from "react";
import axios from "axios";

const Recomendacion = () => {
  const [pelicula, setPelicula] = useState("");
  const [recomendaciones, setRecomendaciones] = useState<
    { titulo: string; similitud: number }[]
  >([]);
  const [loading, setLoading] = useState(false);
  const [buscado, setBuscado] = useState(false); // Saber si ya se intentó buscar

  const obtenerRecomendaciones = async () => {
    setLoading(true);
    setBuscado(true);
    try {
      const res = await axios.post("http://localhost:5000/api/recomendacion", {
        pelicula,
      });
      setRecomendaciones(res.data);
    } catch (error) {
      console.error("Error al obtener recomendaciones", error);
      setRecomendaciones([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>Recomendador por Descripción</h1>
      <input
        type="text"
        value={pelicula}
        onChange={(e) => setPelicula(e.target.value)}
        placeholder="Nombre de la película"
      />
      <button onClick={obtenerRecomendaciones}>Buscar</button>

      {loading && (
        <div style={{ marginTop: "1rem" }}>
          <span className="spinner" style={{ fontSize: "1rem" }}>
            ⏳
          </span>{" "}
          Buscando recomendaciones...
        </div>
      )}

      {!loading && recomendaciones.length > 0 && (
        <ul>
          {recomendaciones.map((r, i) => (
            <li key={i}>
              {r.titulo} (Similitud: {(r.similitud * 100).toFixed(2)}%)
            </li>
          ))}
        </ul>
      )}

      {!loading && buscado && recomendaciones.length === 0 && (
        <p>No se encontraron recomendaciones.</p>
      )}
    </div>
  );
};

export default Recomendacion;
