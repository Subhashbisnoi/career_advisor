import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Header from './components/Header';
import Home from './components/Home';
import Interview from './components/Interview';
import Results from './components/Results';
import './App.css';

function App() {
  const [currentSession, setCurrentSession] = useState(null);
  const [interviewData, setInterviewData] = useState(null);

  const startNewInterview = (data) => {
    setInterviewData(data);
    setCurrentSession(null);
  };

  const setSession = (session) => {
    setCurrentSession(session);
  };

  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Header />
        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route 
              path="/" 
              element={<Home onStartInterview={startNewInterview} />} 
            />
            <Route 
              path="/interview" 
              element={
                interviewData ? (
                  <Interview 
                    interviewData={interviewData} 
                    onSessionCreated={setSession}
                  />
                ) : (
                  <Navigate to="/" replace />
                )
              } 
            />
            <Route 
              path="/results" 
              element={
                currentSession ? (
                  <Results session={currentSession} />
                ) : (
                  <Navigate to="/" replace />
                )
              } 
            />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;