import { Routes, Route } from 'react-router-dom';
import './App.css';
import Home from './pages/Home';
import Datos from './pages/Datos';
import Login from './pages/Login';
import Registro from './pages/Registro';
import Pelis from './pages/Pelis';
import RutaPrivada from './components/RutaPrivada';
import NoEncontrado from './pages/NoEncontrado';

const App = () => {
  return (
    <Routes>
      <Route path="*" element={<NoEncontrado />} />
      <Route path="/" element={<Home />} />
      <Route path="/datos" element={<Datos />} />
      <Route path="/login" element={<Login />} />
      <Route path="/registro" element={<Registro />} />
      <Route
        path="/pelis"
        element={
          <RutaPrivada>
            <Pelis />
          </RutaPrivada>
        }
      />
    </Routes>
  );
};

export default App;
