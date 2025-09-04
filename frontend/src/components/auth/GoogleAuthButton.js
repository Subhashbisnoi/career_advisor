import React, { useEffect, useRef } from 'react';
import { useAuth } from '../../contexts/AuthContext';

const GoogleAuthButton = ({ text = "Continue with Google" }) => {
  const googleButtonRef = useRef(null);
  const { googleLogin } = useAuth();

  const handleCredentialResponse = async (response) => {
    try {
      await googleLogin(response.credential);
    } catch (error) {
      console.error('Google login failed:', error);
    }
  };

  useEffect(() => {
    // Load Google Identity Services script
    const script = document.createElement('script');
    script.src = 'https://accounts.google.com/gsi/client';
    script.async = true;
    script.defer = true;
    
    script.onload = () => {
      // Initialize Google Sign-In
      if (window.google && process.env.REACT_APP_GOOGLE_CLIENT_ID) {
        window.google.accounts.id.initialize({
          client_id: process.env.REACT_APP_GOOGLE_CLIENT_ID,
          callback: handleCredentialResponse,
        });

        // Render the Google Sign-In button
        if (googleButtonRef.current) {
          window.google.accounts.id.renderButton(googleButtonRef.current, {
            theme: "outline",
            size: "large",
            text: "continue_with",
            width: "100%",
          });
        }
      }
    };
    
    document.head.appendChild(script);

    // Cleanup
    return () => {
      const existingScript = document.querySelector('script[src*="gsi/client"]');
      if (existingScript) {
        document.head.removeChild(existingScript);
      }
    };
  }, []);

  if (!process.env.REACT_APP_GOOGLE_CLIENT_ID) {
    return (
      <div className="text-sm text-gray-500 text-center py-2">
        Google OAuth not configured
      </div>
    );
  }

  return (
    <div 
      ref={googleButtonRef} 
      className="w-full"
    ></div>
  );
};

export default GoogleAuthButton;
