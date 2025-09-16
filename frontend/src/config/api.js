// API Configuration
export const API_URL = process.env.REACT_APP_API_URL || 'https://career-advisor-backend-yies.onrender.com';

// Make sure we always have a valid API URL
console.log('[API CONFIG] Using API URL:', API_URL);

export default API_URL;
