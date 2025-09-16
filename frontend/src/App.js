import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Header from './components/Header';
import Home from './components/Home';
import Assessment from './components/Assessment';
import Results from './components/Results';
import Dashboard from './components/Dashboard';
import CareerRoadmap from './components/CareerRoadmap';
import ProtectedRoute from './components/auth/ProtectedRoute';
import './App.css';

// Component to handle OAuth callbacks
const OAuthHandler = () => {
  const { githubLogin } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const handleGitHubCallback = async () => {
      const urlParams = new URLSearchParams(location.search);
      const code = urlParams.get('code');
      const state = urlParams.get('state');
      
      if (code && state === 'github-auth') {
        try {
          console.log('Handling GitHub OAuth callback with code:', code);
          const result = await githubLogin(code);
          
          // Clean up URL parameters
          window.history.replaceState({}, document.title, window.location.pathname);
          
          if (result.success) {
            console.log('GitHub login successful, navigating to home');
            navigate('/', { replace: true });
          } else {
            console.error('GitHub login failed:', result.error);
            // Stay on current page and show error
          }
        } catch (error) {
          console.error('GitHub OAuth callback error:', error);
          // Stay on current page and show error
        }
      }
    };

    handleGitHubCallback();
  }, [location.search, githubLogin, navigate]);

  return null; // This component doesn't render anything
};

// Wrapper component to handle protected routes
const AppContent = () => {
  const [currentAssessment, setCurrentAssessment] = useState(null);
  const [assessmentData, setAssessmentData] = useState(null);
  const [careerResults, setCareerResults] = useState(null);
  const { user } = useAuth();

  const startNewAssessment = (data) => {
    setAssessmentData(data);
    setCurrentAssessment(null);
    setCareerResults(null);
  };

  const setAssessment = (assessment) => {
    setCurrentAssessment(assessment);
  };

  const setResults = (results) => {
    setCareerResults(results);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <OAuthHandler />
      <Header />
      <main className="container mx-auto px-4 py-8">
        <Routes>
          <Route 
            path="/" 
            element={<Home onStartAssessment={startNewAssessment} />} 
          />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/roadmap"
            element={
              <ProtectedRoute>
                <CareerRoadmap />
              </ProtectedRoute>
            }
          />
          <Route
            path="/assessment"
            element={
              <ProtectedRoute>
                {assessmentData ? (
                  <Assessment 
                    assessmentData={assessmentData} 
                    onAssessmentCreated={setAssessment}
                    onResultsGenerated={setResults}
                  />
                ) : (
                  <Navigate to="/" replace />
                )}
              </ProtectedRoute>
            }
          />
          <Route
            path="/results"
            element={
              <ProtectedRoute>
                {careerResults ? (
                  <Results results={careerResults} />
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