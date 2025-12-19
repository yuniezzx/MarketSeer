import { Link, useLocation } from 'react-router-dom';
import { Home, List, TrendingUp } from 'lucide-react';

function Navbar() {
  const location = useLocation();

  const isActive = path => {
    return location.pathname === path;
  };

  return (
    <nav className='bg-white dark:bg-gray-800 shadow-md'>
      <div className='max-w-7xl mx-auto px-4 sm:px-6 lg:px-8'>
        <div className='flex items-center justify-between h-16'>
          {/* Logo/Brand */}
          <div className='shrink-0'>
            <h1 className='text-xl font-bold text-gray-900 dark:text-white'>MarketSeer</h1>
          </div>

          {/* Navigation Links */}
          <div className='flex space-x-4'>
            <Link
              to='/'
              className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors ${isActive('/') ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-200' : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                }`}>
              <Home className='w-4 h-4 mr-2' />
              Home
            </Link>

            <Link
              to='/stocks'
              className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors ${isActive('/stocks') ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-200' : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                }`}>
              <List className='w-4 h-4 mr-2' />
              Stock List
            </Link>

            <Link
              to='/dragon-tiger'
              className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors ${isActive('/dragon-tiger') ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-200' : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                }`}>
              <TrendingUp className='w-4 h-4 mr-2' />
              龙虎榜
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
