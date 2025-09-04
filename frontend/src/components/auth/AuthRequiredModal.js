import React from 'react';
import { X } from 'lucide-react';

const AuthRequiredModal = ({ isOpen, onClose, onLogin, onSignup }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
        <div className="p-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-medium text-gray-900">Sign In Required</h3>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-500 focus:outline-none"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
          
          <div className="mt-2">
            <p className="text-sm text-gray-600">
              Please sign in to view your interview results and personalized feedback.
            </p>
          </div>

          <div className="mt-6 flex flex-col sm:flex-row-reverse sm:space-x-3 sm:space-x-reverse">
            <button
              type="button"
              onClick={onLogin}
              className="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-indigo-600 text-base font-medium text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:ml-3 sm:w-auto sm:text-sm"
            >
              Sign In
            </button>
            <button
              type="button"
              onClick={onSignup}
              className="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
            >
              Create Account
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AuthRequiredModal;
