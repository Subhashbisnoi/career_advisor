import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Header from './components/Header';
import Home from './components/Home';
import Interview from './components/Interview';
import InterviewDashboard from './components/dashboard/InterviewDashboard';
import Result from './components/Result';
import LoginPage from './pages/LoginPage';
import SignupPage from './pages/SignupPage';
import ProtectedRoute from './components/auth/ProtectedRoute';
import './App.css';

// Wrapper component to handle protected routes
const AppContent = () => {
  const [currentSession, setCurrentSession] = useState(null);
  const [interviewData, setInterviewData] = useState(null);
  const { user } = useAuth();

  const startNewInterview = (data) => {
    setInterviewData(data);
    setCurrentSession(null);
  };

  const setSession = (session) => {
    setCurrentSession(session);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <main className="container mx-auto px-4 py-8">
        <Routes>
          <Route 
            path="/" 
            element={<Home onStartInterview={startNewInterview} />} 
          />
          <Route 
            path="/login" 
            element={<LoginPage />} 
          />
          <Route 
            path="/signup" 
            element={<SignupPage />} 
          />
          <Route
            path="/interview"
            element={
              <ProtectedRoute>
                {interviewData ? (
                  <Interview 
                    interviewData={interviewData} 
                    onSessionCreated={setSession}
                  />
                ) : (
                  <Navigate to="/" replace />
                )}
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <InterviewDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/results"
            element={
              <ProtectedRoute>
                {currentSession ? (
                  <Result session={currentSession} />
                ) : (
                  <Navigate to="/" replace />
                )}
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  );
};

function App() {
  return (
    <Router>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </Router>
  );
}

export default App;