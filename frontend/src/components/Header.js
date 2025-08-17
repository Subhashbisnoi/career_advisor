import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Brain, Home, BarChart3 } from 'lucide-react';

const Header = () => {
  const location = useLocation();

  const isActive = (path) => {
    return location.pathname === path;
  };

  return (
    <header className="bg-white shadow-sm border-b">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-3">
            <Brain className="h-8 w-8 text-primary-600" />
            <h1 className="text-xl font-bold text-gray-900">AI Interviewer</h1>
          </div>
          
          <nav className="flex space-x-8">
            <Link
              to="/"
              className={`flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                isActive('/') 
                  ? 'text-primary-600 bg-primary-50' 
                  : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
              }`}
            >
              <Home className="h-4 w-4" />
              <span>Home</span>
            </Link>
            
            {location.pathname === '/interview' && (
              <Link
                to="/interview"
                className="flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium text-primary-600 bg-primary-50"
              >
                <Brain className="h-4 w-4" />
                <span>Interview</span>
              </Link>
            )}
            
            {location.pathname === '/results' && (
              <Link
                to="/results"
                className="flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium text-primary-600 bg-primary-50"
              >
                <BarChart3 className="h-4 w-4" />
                <span>Results</span>
              </Link>
            )}
          </nav>
        </div>
      </div>
    </header>
  );
};

export default Header;