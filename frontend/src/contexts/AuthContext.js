import React, { createContext, useContext, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { login as loginApi, signup as signupApi, googleAuth as googleAuthApi, githubAuth as githubAuthApi, getCurrentUser } from '../services/auth';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    // Check for existing session on initial load
    const checkAuth = async () => {
      try {
        const token = localStorage.getItem('token');
        if (token) {
          const userData = await getCurrentUser();
          setUser(userData);
        }
      } catch (error) {
        console.error('Auth check failed:', error);
        localStorage.removeItem('token');
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  const login = async (email, password) => {
    try {
      const { user: userData, token } = await loginApi(email, password);
      localStorage.setItem('token', token);
      setUser(userData);
      // Don't navigate automatically - let components handle it
      return { success: true };
    } catch (error) {
      console.error('Login failed:', error);
      return { success: false, error: error.message };
    }
  };

  const signup = async (userData) => {
    try {
      const response = await signupApi(userData);
      
      // The backend now returns token and user data directly on signup
      if (response.access_token && response.user) {
        localStorage.setItem('token', response.access_token);
        setUser(response.user);
        // Don't navigate automatically - let components handle it
        return { success: true };
      }
      
      return { success: false, error: 'Unexpected response from server' };
    } catch (error) {
      console.error('Signup failed:', error);
      throw error; // Let the component handle the error
    }
  };

  const googleLogin = async (credential) => {
    try {
      const { user: userData, token } = await googleAuthApi(credential);
      localStorage.setItem('token', token);
      setUser(userData);
      // Don't navigate automatically - let components handle it
      return { success: true };
    } catch (error) {
      console.error('Google login failed:', error);
      return { success: false, error: error.message };
    }
  };

  const githubLogin = async (code) => {
    try {
      const { user: userData, token } = await githubAuthApi(code);
      localStorage.setItem('token', token);
      setUser(userData);
      // Don't navigate automatically - let components handle it
      return { success: true };
    } catch (error) {
      console.error('GitHub login failed:', error);
      return { success: false, error: error.message };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
    navigate('/');
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, signup, googleLogin, githubLogin, logout }}>
      {!loading && children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext;
