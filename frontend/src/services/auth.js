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

export const getCurrentUser = async () => {
  const token = localStorage.getItem('token');
  if (!token) return null;

  const response = await fetch(`${API_URL}/auth/me`, {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    localStorage.removeItem('token');
    return null;
  }

  return response.json();
};

export const getAuthHeader = () => {
  const token = localStorage.getItem('token');
  return token ? { 'Authorization': `Bearer ${token}` } : {};
};
