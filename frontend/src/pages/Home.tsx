import { Link } from 'react-router-dom';
import BotonAuth from '../components/BotonAuth';

const Home = () => {
  return (
    <div>
      <h1>Bienvenido</h1>
      <Link to="/datos">Ver Usuarios</Link>
      <BotonAuth />
    </div>
  );
};

export default Home;
