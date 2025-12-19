import { Routes, Route } from 'react-router-dom';
import Navbar from './components/shared/Navbar';
import Home from './pages/Home';
import StockList from './pages/StockList';
import DragonTiger from './pages/DragonTiger';

function App() {
  return (
    <div>
      {/* Navigation */}
      <Navbar />

      {/* Routes */}
      <Routes>
        <Route path='/' element={<Home />} />
        <Route path='/stocks' element={<StockList />} />
        <Route path='/dragon-tiger' element={<DragonTiger />} />
      </Routes>
    </div>
  );
}

export default App;
