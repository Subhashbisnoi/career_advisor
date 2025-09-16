import React, { useState } from 'react';

const PinButton = ({ sessionId, isPinned: initialPinned = false, onPinChange }) => {
  const [isPinned, setIsPinned] = useState(initialPinned);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const togglePin = async () => {
    try {
      setLoading(true);
      setError('');
      
      const token = localStorage.getItem('token');
      if (!token) {
        setError('Please log in to pin results');
        return;
      }

      if (!sessionId) {
        setError('Session ID is missing');
        return;
      }

      const endpoint = isPinned 
        ? `http://localhost:8000/interview/unpin/${sessionId}`
        : `http://localhost:8000/interview/pin/${sessionId}`;

      console.log('Pin request:', { endpoint, sessionId, isPinned }); // Debug log

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const newPinnedState = !isPinned;
        setIsPinned(newPinnedState);
        
        // Notify parent component about pin status change
        if (onPinChange) {
          onPinChange(sessionId, newPinnedState);
        }
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to update pin status');
      }
    } catch (err) {
      setError('Network error occurred');
      console.error('Error toggling pin:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative flex flex-col items-center space-y-1">
      <button
        onClick={togglePin}
        disabled={loading}
        className={`
          relative p-2 rounded-full transition-all duration-200 
          ${loading ? 'opacity-50 cursor-not-allowed' : 'hover:scale-110'}
          ${isPinned 
            ? 'bg-red-100 text-red-600 hover:bg-red-200' 
            : 'bg-gray-100 text-gray-600 hover:bg-indigo-100 hover:text-indigo-600'
          }
        `}
        title={isPinned ? 'Unpin this result' : 'Pin this result'}
      >
        {loading ? (
          <div className="w-6 h-6 animate-spin border-2 border-current border-t-transparent rounded-full"></div>
        ) : (
          <svg 
            className={`w-6 h-6 transition-transform ${isPinned ? 'rotate-45' : ''}`} 
            fill={isPinned ? 'currentColor' : 'none'}
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            {isPinned ? (
              // Filled pin icon (pinned state)
              <path 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                strokeWidth={2} 
                d="M12 2L9 8v6l-3 3v1h12v-1l-3-3V8l-3-6z"
                fill="currentColor"
              />
            ) : (
              // Outline pin icon (unpinned state)
              <path 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                strokeWidth={2} 
                d="M12 2L9 8v6l-3 3v1h12v-1l-3-3V8l-3-6z"
              />
            )}
          </svg>
        )}
      </button>
      
      <span className={`text-xs font-medium transition-colors ${
        isPinned ? 'text-red-600' : 'text-gray-500'
      }`}>
        {isPinned ? 'Pinned' : 'Pin'}
      </span>
      
      {error && (
        <div className="absolute top-full mt-2 left-1/2 transform -translate-x-1/2 p-2 bg-red-100 text-red-700 text-xs rounded shadow-lg z-10 whitespace-nowrap">
          {error}
        </div>
      )}
    </div>
  );
};

export default PinButton;
