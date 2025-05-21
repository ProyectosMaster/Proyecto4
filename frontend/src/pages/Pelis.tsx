import BotonAuth from '../components/BotonAuth';

const Pelis = () => {
  return (
    <div>
      <h1>Página protegida de Pelis 🎬</h1>
      <p>Solo puedes verla si iniciaste sesión.</p>
      <BotonAuth />
    </div>
  );
};

export default Pelis;
