import { useState, useEffect } from "react";
import axios from "axios";

const Recomendacion = () => {
  const [pelicula, setPelicula] = useState("");
  const [recomendaciones, setRecomendaciones] = useState<
    { titulo: string; similitud: number }[]
  >([]);
  const [loading, setLoading] = useState(false);
  const [buscado, setBuscado] = useState(false);
  const [sugerencias, setSugerencias] = useState<string[]>([]);

  const obtenerRecomendaciones = async () => {
    setLoading(true);
    setBuscado(true);
    setSugerencias([]); // limpiar sugerencias al buscar
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

  // Obtener sugerencias al escribir
  useEffect(() => {
    const fetchSugerencias = async () => {
      if (pelicula.length < 2) {
        setSugerencias([]);
        return;
      }

      try {
        const res = await axios.get("http://localhost:5000/api/sugerencias", {
          params: { q: pelicula },
        });
        setSugerencias(res.data);
      } catch (error) {
        console.error("Error al obtener sugerencias", error);
      }
    };

    const timeout = setTimeout(fetchSugerencias, 300); // esperar 300ms
    return () => clearTimeout(timeout);
  }, [pelicula]);

  const handleSugerenciaClick = (titulo: string) => {
    setPelicula(titulo);
    setSugerencias([]);
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

      {/* Mostrar sugerencias */}
      {sugerencias.length > 0 && (
        <ul style={{ background: "#f0f0f0", border: "1px solid #ccc" }}>
          {sugerencias.map((sug, i) => (
            <li
              key={i}
              onClick={() => handleSugerenciaClick(sug)}
              style={{ cursor: "pointer", padding: "0.5rem" }}
            >
              {sug}
            </li>
          ))}
        </ul>
      )}

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
