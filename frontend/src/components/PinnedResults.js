import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Home, Download, Star, TrendingUp, Target, CheckCircle, AlertCircle, XCircle } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import PinButton from './PinButton';

const PinnedResults = () => {
  const [pinnedSessions, setPinnedSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedSession, setSelectedSession] = useState(null);
  const { user } = useAuth();

  useEffect(() => {
    if (user) {
      fetchPinnedSessions();
    }
  }, [user]);

  const fetchPinnedSessions = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/interview/pinned', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setPinnedSessions(data.pinned_sessions || []);
      } else {
        setError('Failed to fetch pinned sessions');
      }
    } catch (err) {
      setError('Network error occurred');
      console.error('Error fetching pinned sessions:', err);
    } finally {
      setLoading(false);
    }
  };

  const unpinSession = async (sessionId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/interview/unpin/${sessionId}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        // Remove from pinned sessions
        setPinnedSessions(prev => prev.filter(session => session.thread_id !== sessionId));
      } else {
        setError('Failed to unpin session');
      }
    } catch (err) {
      setError('Network error occurred');
      console.error('Error unpinning session:', err);
    }
  };

  const getScoreColor = (score) => {
    if (score >= 8) return 'text-green-600';
    if (score >= 6) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreIcon = (score) => {
    if (score >= 8) return <CheckCircle className="h-5 w-5 text-green-500" />;
    if (score >= 6) return <AlertCircle className="h-5 w-5 text-yellow-500" />;
    return <XCircle className="h-5 w-5 text-red-500" />;
  };

  const getFeedbackBorderClass = (score) => {
    if (score >= 8) return 'feedback-positive';
    if (score >= 6) return 'feedback-neutral';
    return 'feedback-negative';
  };

  const downloadResults = (session) => {
    const resultsText = `
AI Interview Results
===================

Role: ${session.role}
Company: ${session.company}

Total Score: ${session.total_score}/30
Average Score: ${session.average_score.toFixed(1)}/10

Feedback: ${session.feedback || 'No detailed feedback available'}

Learning Roadmap:
${session.roadmap || 'No roadmap available'}
    `;

    const blob = new Blob([resultsText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `interview-results-${session.role}-${session.company}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Please log in</h2>
          <p className="text-gray-600">You need to be logged in to view your pinned results.</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
    
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        

        {error && (
          <div className="mb-6 bg-red-50 border-l-4 border-red-400 p-4">
            <div className="flex">
              <div className="ml-3">
                <p className="text-sm text-red-700">{error}</p>
              </div>
            </div>
          </div>
        )}

  
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {!selectedSession && (
          <>
            <div className="mb-8">
              <h1 className="text-3xl font-bold text-gray-900">📌 Pinned Results</h1>
              <p className="mt-2 text-gray-600">Your saved interview results that you can access anytime.</p>
            </div>

            {error && (
              <div className="mb-6 bg-red-50 border-l-4 border-red-400 p-4">
                <div className="flex">
                  <div className="ml-3">
                    <p className="text-sm text-red-700">{error}</p>
                  </div>
                </div>
              </div>
            )}

            {pinnedSessions.length === 0 ? (
              <div className="text-center py-12">
                <div className="text-6xl mb-4">📌</div>
                <h2 className="text-2xl font-bold text-gray-900 mb-4">No Pinned Results</h2>
                <p className="text-gray-600 mb-6">
                  Pin your interview results to save them for future reference. 
                  Pinned results will stay here even after you navigate away from the results page.
                </p>
                <p className="text-sm text-gray-500">
                  Complete an interview and use the pin button on the results page to save important results.
                </p>
              </div>
            ) : (
              <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                {pinnedSessions.map((session) => (
                  <div key={session.thread_id} className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
                    <div className="flex justify-between items-start mb-4">
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold text-gray-900 mb-1">
                          {session.role} at {session.company}
                        </h3>
                        <p className="text-sm text-gray-500">{formatDate(session.created_at)}</p>
                      </div>
                      <button
                        onClick={() => unpinSession(session.thread_id)}
                        className="text-red-500 hover:text-red-700 transition-colors"
                        title="Unpin this result"
                      >
                        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" clipRule="evenodd" />
                        </svg>
                      </button>
                    </div>

                    {session.average_score > 0 && (
                      <div className="mb-4">
                        <div className="flex items-center justify-between">
                          <span className="text-sm font-medium text-gray-700">Score</span>
                          <span className="text-lg font-bold text-indigo-600">
                            {session.average_score.toFixed(1)}/10
                          </span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
                          <div
                            className="bg-indigo-600 h-2 rounded-full"
                            style={{ width: `${(session.average_score / 10) * 100}%` }}
                          ></div>
                        </div>
                      </div>
                    )}

                    <div className="space-y-3">
                      {session.feedback && (
                        <div>
                          <h4 className="text-sm font-semibold text-gray-700 mb-1">Feedback</h4>
                          <p className="text-sm text-gray-600 line-clamp-3">{session.feedback.substring(0, 100)}...</p>
                        </div>
                      )}

                      {session.roadmap && (
                        <div>
                          <h4 className="text-sm font-semibold text-gray-700 mb-1">Roadmap</h4>
                          <p className="text-sm text-gray-600 line-clamp-3">{session.roadmap.substring(0, 100)}...</p>
                        </div>
                      )}
                    </div>

                    <button
                      onClick={() => setSelectedSession(session)}
                      className="mt-4 w-full bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 transition-colors text-sm font-medium"
                    >
                      View Full Results
                    </button>
                  </div>
                ))}
              </div>
            )}
          </>
        )}

        {/* Full Result View - Only shows when a session is selected */}
        {selectedSession && (
          <div className="max-w-6xl mx-auto">
            {/* Back Button */}
            <div className="mb-6">
              <button
                onClick={() => setSelectedSession(null)}
                className="flex items-center space-x-2 text-indigo-600 hover:text-indigo-700 transition-colors"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
                <span>Back to Pinned Results</span>
              </button>
            </div>

            {/* Header - Same as Result component */}
            <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h1 className="text-3xl font-bold text-gray-900 mb-2">Interview Results</h1>
                  <p className="text-xl text-gray-600">
                    {selectedSession.role} at {selectedSession.company}
                  </p>
                </div>
                <div className="flex items-center space-x-4">
                  <PinButton 
                    sessionId={selectedSession.thread_id} 
                    isPinned={true}
                    onPinChange={(sessionId, isPinned) => {
                      if (!isPinned) {
                        // Remove from pinned sessions if unpinned
                        setPinnedSessions(prev => prev.filter(s => s.thread_id !== sessionId));
                        setSelectedSession(null); // Go back to list
                      }
                    }}
                  />
                  <button
                    onClick={() => downloadResults(selectedSession)}
                    className="flex items-center space-x-2 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
                  >
                    <Download className="h-4 w-4" />
                    <span>Download Results</span>
                  </button>
                </div>
              </div>

              {/* Score Summary - Same as Result component */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-lg p-6 text-center">
                  <div className="text-3xl font-bold mb-2">{selectedSession.total_score || 0}/30</div>
                  <div className="text-blue-100">Total Score</div>
                </div>
                <div className="bg-gradient-to-r from-green-500 to-green-600 text-white rounded-lg p-6 text-center">
                  <div className="text-3xl font-bold mb-2">{selectedSession.average_score ? selectedSession.average_score.toFixed(1) : '0.0'}/10</div>
                  <div className="text-green-100">Average Score</div>
                </div>
                <div className="bg-gradient-to-r from-purple-500 to-purple-600 text-white rounded-lg p-6 text-center">
                  <div className="text-3xl font-bold mb-2">3</div>
                  <div className="text-purple-100">Questions</div>
                </div>
              </div>
            </div>

            {/* Tabs - Same as Result component */}
            <div className="bg-white rounded-lg shadow-lg mb-8">
              <div className="border-b border-gray-200">
                <nav className="flex space-x-8 px-8">
                  <button
                    className="py-4 px-1 border-b-2 border-primary-500 text-primary-600 font-medium text-sm"
                  >
                    <div className="flex items-center space-x-2">
                      <Star className="h-4 w-4" />
                      <span>Results Details</span>
                    </div>
                  </button>
                </nav>
              </div>

              <div className="p-8">
                <div className="space-y-6">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-500">{formatDate(selectedSession.created_at)}</span>
                    {selectedSession.average_score > 0 && (
                      <span className="text-xl font-bold text-indigo-600">
                        Score: {selectedSession.average_score.toFixed(1)}/10
                      </span>
                    )}
                  </div>

                  {selectedSession.feedback && (
                    <div>
                      <h2 className="text-2xl font-bold text-gray-900 mb-6">📝 Overall Feedback</h2>
                      <div className="bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200 rounded-lg p-6">
                        <div className="prose prose-lg max-w-none">
                          <p className="text-gray-700 whitespace-pre-wrap">{selectedSession.feedback}</p>
                        </div>
                      </div>
                    </div>
                  )}

                  {selectedSession.roadmap && (
                    <div>
                      <h2 className="text-2xl font-bold text-gray-900 mb-6">🗺️ Personalized Learning Roadmap</h2>
                      <div className="bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200 rounded-lg p-6">
                        <div className="roadmap-content prose prose-lg max-w-none">
                          <ReactMarkdown>{selectedSession.roadmap}</ReactMarkdown>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Action Cards - Same as Result component */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
              <div className="bg-white rounded-lg shadow-lg p-6">
                <div className="flex items-center space-x-3 mb-4">
                  <div className="bg-green-100 rounded-full p-2">
                    <CheckCircle className="h-6 w-6 text-green-600" />
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900">Pinned Result</h3>
                </div>
                <p className="text-gray-600">
                  This result has been pinned for future reference. You can access it anytime from the pinned results section.
                </p>
              </div>

              <div className="bg-white rounded-lg shadow-lg p-6">
                <div className="flex items-center space-x-3 mb-4">
                  <div className="bg-yellow-100 rounded-full p-2">
                    <TrendingUp className="h-6 w-6 text-yellow-600" />
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900">Keep Improving</h3>
                </div>
                <p className="text-gray-600">
                  Use the learning roadmap to continue improving your skills. Practice makes perfect!
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
      </div>
    </div>
  );
};

export default PinnedResults;
