/**
 * Enhanced Interview Service with state management and threading support
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
 * Start a new interview session
 */
export const startInterviewSession = async (interviewData) => {
  try {
    const response = await fetch(`${API_URL}/interview/v2/start`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({
        role: interviewData.role,
        company: interviewData.company,
        resume_text: interviewData.resume_text
      }),
    });

    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.detail || data.message || 'Failed to start interview');
    }

    return data;
  } catch (error) {
    console.error('Start interview error:', error);
    throw error;
  }
};

/**
 * Submit an answer for a specific question
 */
export const submitAnswer = async (threadId, questionNumber, answer) => {
  try {
    const response = await fetch(`${API_URL}/interview/v2/submit-answer`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({
        thread_id: threadId,
        question_number: questionNumber,
        answer: answer
      }),
    });

    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.detail || data.message || 'Failed to submit answer');
    }

    return data;
  } catch (error) {
    console.error('Submit answer error:', error);
    throw error;
  }
};

/**
 * Get chat history for an interview session
 */
export const getChatHistory = async (threadId) => {
  try {
    const response = await fetch(`${API_URL}/interview/v2/chat-history/${threadId}`, {
      method: 'GET',
      headers: getAuthHeaders(),
    });

    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.detail || data.message || 'Failed to get chat history');
    }

    return data;
  } catch (error) {
    console.error('Get chat history error:', error);
    throw error;
  }
};

/**
 * Get all interview sessions for the current user
 */
export const getUserInterviewSessions = async () => {
  try {
    const response = await fetch(`${API_URL}/interview/v2/sessions`, {
      method: 'GET',
      headers: getAuthHeaders(),
    });

    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.detail || data.message || 'Failed to get interview sessions');
    }

    return data;
  } catch (error) {
    console.error('Get interview sessions error:', error);
    throw error;
  }
};

/**
 * Get status and progress of an interview session
 */
export const getSessionStatus = async (threadId) => {
  try {
    const response = await fetch(`${API_URL}/interview/v2/session/${threadId}/status`, {
      method: 'GET',
      headers: getAuthHeaders(),
    });

    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.detail || data.message || 'Failed to get session status');
    }

    return data;
  } catch (error) {
    console.error('Get session status error:', error);
    throw error;
  }
};

/**
 * Delete an interview session
 */
export const deleteInterviewSession = async (threadId) => {
  try {
    const response = await fetch(`${API_URL}/interview/v2/session/${threadId}`, {
      method: 'DELETE',
      headers: getAuthHeaders(),
    });

    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.detail || data.message || 'Failed to delete interview session');
    }

    return data;
  } catch (error) {
    console.error('Delete interview session error:', error);
    throw error;
  }
};

/**
 * Get user analytics and performance metrics
 */
export const getUserAnalytics = async () => {
  try {
    const response = await fetch(`${API_URL}/interview/v2/analytics`, {
      method: 'GET',
      headers: getAuthHeaders(),
    });

    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.detail || data.message || 'Failed to get analytics');
    }

    return data;
  } catch (error) {
    console.error('Get analytics error:', error);
    throw error;
  }
};

/**
 * Upload resume and extract text
 */
export const uploadResume = async (file) => {
  try {
    const formData = new FormData();
    formData.append('file', file);

    const token = localStorage.getItem('token');
    const headers = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_URL}/interview/upload-resume`, {
      method: 'POST',
      headers: headers,
      body: formData,
    });

    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.detail || data.message || 'Failed to upload resume');
    }

    return data;
  } catch (error) {
    console.error('Upload resume error:', error);
    throw error;
  }
};

/**
 * Format chat messages for display
 */
export const formatChatHistory = (chatHistory) => {
  if (!chatHistory || !chatHistory.messages) {
    return [];
  }

  return chatHistory.messages.map(message => ({
    id: message.id,
    type: message.type,
    role: message.role,
    content: message.content,
    questionNumber: message.question_number,
    marks: message.marks,
    timestamp: new Date(message.created_at),
    metadata: message.metadata
  }));
};

/**
 * Calculate progress percentage
 */
export const calculateProgress = (sessionStatus) => {
  if (!sessionStatus) return 0;
  
  const { answers_submitted = 0, total_questions = 3 } = sessionStatus;
  return Math.round((answers_submitted / total_questions) * 100);
};

/**
 * Get status color for UI
 */
export const getStatusColor = (status) => {
  switch (status) {
    case 'active':
    case 'in_progress':
      return 'text-blue-600';
    case 'completed':
      return 'text-green-600';
    case 'archived':
      return 'text-gray-600';
    default:
      return 'text-gray-600';
  }
};

/**
 * Format score for display
 */
export const formatScore = (score) => {
  if (typeof score !== 'number') return '0.0';
  return score.toFixed(1);
};
