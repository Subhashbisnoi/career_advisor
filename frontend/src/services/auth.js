const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const login = async (email, password) => {
  try {
    const response = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams({
        username: email,
        password: password,
      }),
    });

    const data = await response.json();
    
    if (!response.ok) {
      // Handle different types of errors
      if (response.status === 422 && data.detail) {
        // Parse Pydantic validation errors
        if (Array.isArray(data.detail)) {
          const validationErrors = data.detail.map(error => {
            if (error.loc && error.msg) {
              const field = error.loc[error.loc.length - 1]; // Get the field name
              return `${field}: ${error.msg}`;
            }
            return error.msg || error.message || 'Validation error';
          });
          throw new Error(validationErrors.join(', '));
        } else {
          throw new Error(data.detail);
        }
      }
      
      throw new Error(data.detail || data.message || 'Login failed');
    }

    // The backend returns {access_token, token_type, user: {email, full_name}}
    return {
      token: data.access_token,
      user: data.user || { email },
    };
  } catch (error) {
    console.error('Login error:', error);
    throw error; // Re-throw the error so the component can handle it
  }
};

export const signup = async (userData) => {
  try {
    const response = await fetch(`${API_URL}/auth/signup`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: userData.email,
        password: userData.password,
        full_name: userData.full_name
      }),
    });

    const data = await response.json();
    
    if (!response.ok) {
      // Handle validation errors properly
      if (response.status === 422 && data.detail) {
        // Parse Pydantic validation errors
        if (Array.isArray(data.detail)) {
          const validationErrors = data.detail.map(error => {
            if (error.loc && error.msg) {
              const field = error.loc[error.loc.length - 1]; // Get the field name
              return `${field}: ${error.msg}`;
            }
            return error.msg || error.message || 'Validation error';
          });
          throw new Error(validationErrors.join(', '));
        } else {
          throw new Error(data.detail);
        }
      }
      
      const errorMessage = data.detail || data.message || 'Signup failed';
      throw new Error(errorMessage);
    }

    return data;
  } catch (error) {
    console.error('Signup error:', error);
    throw error; // Re-throw the error so the component can handle it
  }
};

export const googleAuth = async (credential) => {
  try {
    const response = await fetch(`${API_URL}/auth/google`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        credential: credential
      }),
    });

    const data = await response.json();
    
    if (!response.ok) {
      if (response.status === 422 && data.detail) {
        if (Array.isArray(data.detail)) {
          const validationErrors = data.detail.map(error => {
            if (error.loc && error.msg) {
              const field = error.loc[error.loc.length - 1];
              return `${field}: ${error.msg}`;
            }
            return error.msg || error.message || 'Validation error';
          });
          throw new Error(validationErrors.join(', '));
        } else {
          throw new Error(data.detail);
        }
      }
      
      throw new Error(data.detail || data.message || 'Google authentication failed');
    }

    return {
      token: data.access_token,
      user: data.user,
    };
  } catch (error) {
    console.error('Google auth error:', error);
    throw error;
  }
};

export const githubAuth = async (code) => {
  try {
    const response = await fetch(`${API_URL}/auth/github`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        code: code
      }),
    });

    const data = await response.json();
    
    if (!response.ok) {
      if (response.status === 422 && data.detail) {
        if (Array.isArray(data.detail)) {
          const validationErrors = data.detail.map(error => {
            if (error.loc && error.msg) {
              const field = error.loc[error.loc.length - 1];
              return `${field}: ${error.msg}`;
            }
            return error.msg || error.message || 'Validation error';
          });
          throw new Error(validationErrors.join(', '));
        } else {
          throw new Error(data.detail);
        }
      }
      
      throw new Error(data.detail || data.message || 'GitHub authentication failed');
    }

    return {
      token: data.access_token,
      user: data.user,
    };
  } catch (error) {
    console.error('GitHub auth error:', error);
    throw error;
  }
};

export const getCurrentUser = async () => {
  const token = localStorage.getItem('token');
  if (!token) return null;

  const response = await fetch(`${API_URL}/auth/me`, {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    if (response.status === 401) {
      // Token might be expired, try to refresh
      const refreshed = await tryRefreshToken();
      if (refreshed) {
        // Retry with new token
        const newToken = localStorage.getItem('token');
        const retryResponse = await fetch(`${API_URL}/auth/me`, {
          headers: {
            'Authorization': `Bearer ${newToken}`,
          },
        });
        
        if (retryResponse.ok) {
          return retryResponse.json();
        }
      }
    }
    
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    return null;
  }

  return response.json();
};

const tryRefreshToken = async () => {
  const token = localStorage.getItem('token');
  if (!token) return false;

  try {
    const response = await fetch(`${API_URL}/auth/refresh`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (response.ok) {
      const data = await response.json();
      localStorage.setItem('token', data.access_token);
      localStorage.setItem('user', JSON.stringify(data.user));
      return true;
    }
  } catch (error) {
    console.error('Token refresh failed:', error);
  }
  
  return false;
};

export const makeAuthenticatedRequest = async (url, options = {}) => {
  const token = localStorage.getItem('token');
  
  if (!token) {
    throw new Error('No authentication token found');
  }

  const headers = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`,
    ...options.headers
  };

  let response = await fetch(url, {
    ...options,
    headers
  });

  // If request fails with 401, try to refresh token and retry
  if (response.status === 401) {
    const refreshed = await tryRefreshToken();
    if (refreshed) {
      const newToken = localStorage.getItem('token');
      headers['Authorization'] = `Bearer ${newToken}`;
      
      response = await fetch(url, {
        ...options,
        headers
      });
    }
  }

  // If still 401 after refresh attempt, logout user
  if (response.status === 401) {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/login';
    throw new Error('Your session has expired. Please log in again.');
  }

  return response;
};

export const getAuthHeader = () => {
  const token = localStorage.getItem('token');
  return token ? { 'Authorization': `Bearer ${token}` } : {};
};
