import { Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import StockList from './pages/StockList';

function App() {
  return (
    <div>
      {/* Navigation */}
      <Navbar />

      {/* Routes */}
      <Routes>
        <Route path='/' element={<Home />} />
        <Route path='/stocks' element={<StockList />} />
      </Routes>
    </div>
  );
}

export default App;
