import { Link } from 'react-router-dom';

function NotFound() {
  return (
    <div className='p-6 text-center'>
      <h1 className='text-4xl font-bold text-gray-900 dark:text-white mb-4'>404</h1>
      <p className='text-gray-600 dark:text-gray-300 mb-4'>Page not found</p>
      <Link to='/' className='text-blue-500 hover:text-blue-700 underline'>
        Go back to Home
      </Link>
    </div>
  );
}

export default NotFound;
