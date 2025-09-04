/**
 * Interview Service for normal interview sessions with database storage
 */

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Get auth headers
const getAuthHeaders = () => {
  const token = localStorage.getItem('token');
  return {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` })
  };
};

/**
 * Get all interview sessions for the current user
 */
export const getUserInterviewSessions = async () => {
  try {
    const response = await fetch(`${API_URL}/interview/sessions`, {
      method: 'GET',
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data.sessions || [];
  } catch (error) {
    console.error('Error fetching user sessions:', error);
    throw error;
  }
};

/**
 * Get chat history for a specific session
 */
export const getChatHistory = async (sessionId) => {
  try {
    const response = await fetch(`${API_URL}/interview/session/${sessionId}/chat`, {
      method: 'GET',
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    
    // Transform the messages to include proper formatting
    const messages = data.messages || [];
    return {
      messages: messages.map(msg => ({
        ...msg,
        timestamp: new Date(msg.timestamp)
      }))
    };
  } catch (error) {
    console.error('Error fetching chat history:', error);
    throw error;
  }
};

/**
 * Get user analytics
 */
export const getUserAnalytics = async () => {
  try {
    const response = await fetch(`${API_URL}/interview/analytics`, {
      method: 'GET',
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching analytics:', error);
    throw error;
  }
};

/**
 * Delete an interview session
 */
export const deleteInterviewSession = async (sessionId) => {
  try {
    const response = await fetch(`${API_URL}/interview/session/${sessionId}`, {
      method: 'DELETE',
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return true;
  } catch (error) {
    console.error('Error deleting session:', error);
    throw error;
  }
};

// Utility functions for formatting
export const getStatusColor = (status) => {
  switch (status) {
    case 'completed':
      return 'text-green-600';
    case 'in_progress':
      return 'text-blue-600';
    case 'abandoned':
      return 'text-red-600';
    default:
      return 'text-gray-600';
  }
};

export const formatScore = (score) => {
  return Math.round(score * 10) / 10;
};
