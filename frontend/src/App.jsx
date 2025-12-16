import { Routes, Route, Link } from 'react-router-dom';
import Home from './pages/Home';
import About from './pages/About';
import NotFound from './pages/NotFound';

function App() {
  return (
    <div className='min-h-screen bg-white dark:bg-gray-900'>
      {/* Navigation */}
      <nav className='bg-gray-800 text-white p-4'>
        <div className='container mx-auto flex gap-6'>
          <Link to='/' className='hover:text-amber-300 transition-colors'>
            Home
          </Link>
          <Link to='/about' className='hover:text-amber-300 transition-colors'>
            About
          </Link>
        </div>
      </nav>

      {/* Routes */}
      <Routes>
        <Route path='/' element={<Home />} />
        <Route path='/about' element={<About />} />
        <Route path='*' element={<NotFound />} />
      </Routes>
    </div>
  );
}

export default App;
