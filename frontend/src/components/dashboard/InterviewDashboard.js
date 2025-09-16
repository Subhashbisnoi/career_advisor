import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { 
  getUserInterviewSessions, 
  getChatHistory, 
  deleteInterviewSession,
  getUserAnalytics,
  getStatusColor,
  formatScore 
} from '../../services/interview';

const InterviewDashboard = () => {
  const { user } = useAuth();
  const [sessions, setSessions] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [selectedSession, setSelectedSession] = useState(null);
  const [chatHistory, setChatHistory] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Load user sessions and analytics on component mount
  useEffect(() => {
    if (user) {
      loadUserSessions();
      loadUserAnalytics();
    }
  }, [user]);

  const loadUserSessions = async () => {
    setIsLoading(true);
    try {
      const result = await getUserInterviewSessions();
      console.log('Sessions result:', result); // Debug log
      setSessions(result || []); // result is already the sessions array
    } catch (err) {
      setError(err.message || 'Failed to load sessions');
    } finally {
      setIsLoading(false);
    }
  };

  const loadUserAnalytics = async () => {
    try {
      const result = await getUserAnalytics();
      console.log('Analytics result:', result); // Debug log
      setAnalytics(result); // Store the result directly, not result.analytics
    } catch (err) {
      console.error('Failed to load analytics:', err);
    }
  };

  const handleViewSession = async (session) => {
    setSelectedSession(session);
    setSidebarOpen(true);
    setIsLoading(true);
    try {
      const history = await getChatHistory(session.thread_id);
      setChatHistory(history);
    } catch (err) {
      setError(err.message || 'Failed to load chat history');
    } finally {
      setIsLoading(false);
    }
  };

  const handleViewResult = async (session) => {
    console.log('handleViewResult called with session:', session); // Debug log
    setSelectedSession(session);
    setSidebarOpen(true);
    setIsLoading(true);
    try {
      // Fetch the feedback and roadmap for this session
      const history = await getChatHistory(session.thread_id);
      setChatHistory(history);
    } catch (err) {
      console.error('Error in handleViewResult:', err); // Debug log
      setError(err.message || 'Failed to load session results');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteSession = async (threadId) => {
    if (!window.confirm('Are you sure you want to delete this interview session?')) {
      return;
    }

    try {
      await deleteInterviewSession(threadId);
      setSessions(sessions.filter(s => s.thread_id !== threadId));
      if (selectedSession && selectedSession.thread_id === threadId) {
        setSelectedSession(null);
        setChatHistory(null);
        setSidebarOpen(false);
      }
    } catch (err) {
      setError(err.message || 'Failed to delete session');
    }
  };

  const renderAnalytics = () => {
    console.log('Analytics data:', analytics); // Debug log
    
    if (!analytics || analytics.total_interviews === 0) {
      return (
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Analytics</h2>
          <p className="text-gray-500">No completed interviews yet. Start your first interview to see analytics!</p>
        </div>
      );
    }

    return (
      <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Your Performance Analytics</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-blue-50 p-4 rounded-lg">
            <h3 className="text-sm font-medium text-blue-600">Total Interviews</h3>
            <p className="text-2xl font-bold text-blue-900">{analytics.total_interviews}</p>
          </div>
          
          <div className="bg-green-50 p-4 rounded-lg">
            <h3 className="text-sm font-medium text-green-600">Average Score</h3>
            <p className="text-2xl font-bold text-green-900">
              {analytics.average_score ? analytics.average_score.toFixed(1) : 'N/A'}/10
            </p>
          </div>
          
          <div className="bg-purple-50 p-4 rounded-lg">
            <h3 className="text-sm font-medium text-purple-600">Best Performance</h3>
            <p className="text-2xl font-bold text-purple-900">
              {analytics.best_score ? analytics.best_score.toFixed(1) : 'N/A'}/10
            </p>
          </div>
        </div>

        <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-2">Companies Interviewed</h4>
            <div className="flex flex-wrap gap-2">
              {(analytics.companies || []).map((company, index) => (
                <span key={`company-${index}-${company}`} className="px-2 py-1 bg-gray-100 text-gray-700 rounded-md text-sm">
                  {company}
                </span>
              ))}
            </div>
          </div>
          
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-2">Roles Interviewed</h4>
            <div className="flex flex-wrap gap-2">
              {(analytics.roles || []).map((role, index) => (
                <span key={`role-${index}-${role}`} className="px-2 py-1 bg-gray-100 text-gray-700 rounded-md text-sm">
                  {role}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  };

  const renderSessionsList = () => {
    console.log('Sessions data in renderSessionsList:', sessions); // Debug log
    
    return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold text-gray-900">Interview Sessions</h2>
        <span className="text-sm text-gray-500">{sessions.length} total sessions</span>
      </div>

      {sessions.length === 0 ? (
        <p className="text-gray-500 text-center py-8">
          No interview sessions yet. Start your first interview!
        </p>
      ) : (
        <div className="space-y-4">
          {sessions.map((session) => (
            <div key={`session-${session.thread_id}-${session.id}`} className="border border-gray-200 rounded-lg p-4">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <h3 className="text-lg font-medium text-gray-900">
                    {session.role} at {session.company}
                  </h3>
                  <div className="mt-1 flex items-center space-x-4 text-sm text-gray-500">
                    <span className={getStatusColor(session.status)}>
                      {session.status}
                    </span>
                    <span>
                      {new Date(session.created_at).toLocaleDateString()}
                    </span>
                    {session.status === 'completed' && (
                      <span className="text-blue-600">
                        Score: {formatScore(session.score)}/10
                      </span>
                    )}
                  </div>
                </div>
                
                <div className="flex space-x-2">
                  {session.status === 'completed' && session.has_results && (
                    <button
                      onClick={() => handleViewResult(session)}
                      className="px-3 py-1 text-sm bg-green-600 text-white rounded-md hover:bg-green-700 flex items-center"
                    >
                      <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
                      </svg>
                      View Results
                    </button>
                  )}
                  <button
                    onClick={() => handleDeleteSession(session.thread_id)}
                    className="px-3 py-1 text-sm bg-red-600 text-white rounded-md hover:bg-red-700"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
    );
  };

  const renderChatSidebar = () => {
    return (
      <>
        {/* Overlay for mobile */}
        {sidebarOpen && (
          <div 
            className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
            onClick={() => setSidebarOpen(false)}
          />
        )}
        
        {/* Sidebar */}
        <div className={`
          fixed inset-y-0 right-0 w-full max-w-2xl bg-white shadow-xl z-50 transform transition-transform duration-300 ease-in-out
          ${sidebarOpen ? 'translate-x-0' : 'translate-x-full'}
          lg:relative lg:translate-x-0 lg:shadow-none lg:z-auto
          ${sidebarOpen ? 'lg:block' : 'lg:hidden'}
        `}>
          <div className="h-full flex flex-col">
            {/* Header */}
            <div className="bg-gray-50 px-6 py-4 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  {selectedSession && (
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">
                        {selectedSession.role} at {selectedSession.company}
                      </h3>
                      <div className="mt-1 flex items-center space-x-4 text-sm">
                        <span className={`font-medium ${getStatusColor(selectedSession.status)}`}>
                          {selectedSession.status}
                        </span>
                        <span className="text-gray-500">
                          {new Date(selectedSession.created_at).toLocaleDateString()}
                        </span>
                        {selectedSession.status === 'completed' && (
                          <span className="text-blue-600 font-medium">
                            Score: {formatScore(selectedSession.score)}/10
                          </span>
                        )}
                      </div>
                    </div>
                  )}
                </div>
                <button
                  onClick={() => {
                    setSidebarOpen(false);
                    setSelectedSession(null);
                    setChatHistory(null);
                  }}
                  className="ml-4 text-gray-400 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded-md p-1"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>

            {/* Results Content - Styled like the Result Component */}
            <div className="flex-1 overflow-y-auto">
              {isLoading ? (
                <div className="flex items-center justify-center h-32">
                  <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                  <span className="ml-2 text-gray-600">Loading results...</span>
                </div>
              ) : chatHistory && chatHistory.messages && chatHistory.messages.length > 0 ? (
                <div className="p-6">
                  {/* Score Summary Cards */}
                  {selectedSession && (
                    <div className="mb-8">
                      <div className="grid grid-cols-3 gap-4">
                        <div className="bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-lg p-4 text-center">
                          <div className="text-2xl font-bold mb-1">{Math.round(selectedSession.score * 3) || 'N/A'}/30</div>
                          <div className="text-blue-100 text-sm">Total Score</div>
                        </div>
                        <div className="bg-gradient-to-r from-green-500 to-green-600 text-white rounded-lg p-4 text-center">
                          <div className="text-2xl font-bold mb-1">{selectedSession.score?.toFixed(1) || 'N/A'}/10</div>
                          <div className="text-green-100 text-sm">Average Score</div>
                        </div>
                        <div className="bg-gradient-to-r from-purple-500 to-purple-600 text-white rounded-lg p-4 text-center">
                          <div className="text-2xl font-bold mb-1">{chatHistory.messages.filter(msg => msg.type === 'feedback').length}</div>
                          <div className="text-purple-100 text-sm">Questions</div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Question-by-Question Feedback */}
                  <div className="mb-8">
                    <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
                      <svg className="w-6 h-6 mr-2 text-yellow-600" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                      </svg>
                      Question-by-Question Feedback
                    </h2>
                    
                    <div className="space-y-6">
                      {chatHistory.messages
                        .filter(msg => msg.type === 'feedback')
                        .map((message, index) => {
                          const getScoreColor = (score) => {
                            if (score >= 8) return 'text-green-600';
                            if (score >= 6) return 'text-yellow-600';
                            return 'text-red-600';
                          };

                          const getScoreIcon = (score) => {
                            if (score >= 8) return (
                              <svg className="h-5 w-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                              </svg>
                            );
                            if (score >= 6) return (
                              <svg className="h-5 w-5 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                              </svg>
                            );
                            return (
                              <svg className="h-5 w-5 text-red-500" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                              </svg>
                            );
                          };

                          const getFeedbackBorderClass = (score) => {
                            if (score >= 8) return 'border-green-200 feedback-positive';
                            if (score >= 6) return 'border-yellow-200 feedback-neutral';
                            return 'border-red-200 feedback-negative';
                          };

                          const correspondingQuestion = chatHistory.messages.find(msg => 
                            msg.type === 'question' && msg.question_number === message.question_number
                          );
                          const correspondingAnswer = chatHistory.messages.find(msg => 
                            msg.type === 'answer' && msg.question_number === message.question_number
                          );

                          return (
                            <div key={index} className={`border rounded-lg p-6 ${getFeedbackBorderClass(message.marks)}`}>
                              <div className="flex items-start justify-between mb-4">
                                <div className="flex items-center space-x-3">
                                  <div className="bg-blue-100 rounded-full p-2">
                                    <svg className="h-5 w-5 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
                                    </svg>
                                  </div>
                                  <span className="text-lg font-semibold text-gray-900">
                                    Question {message.question_number}
                                  </span>
                                </div>
                                <div className="flex items-center space-x-2">
                                  {getScoreIcon(message.marks)}
                                  <span className={`text-xl font-bold ${getScoreColor(message.marks)}`}>
                                    {message.marks}/10
                                  </span>
                                </div>
                              </div>
                              
                              {correspondingQuestion && (
                                <div className="mb-4">
                                  <h3 className="font-medium text-gray-900 mb-2">Question:</h3>
                                  <p className="text-gray-700 leading-relaxed">{correspondingQuestion.content}</p>
                                </div>
                              )}
                              
                              {correspondingAnswer && (
                                <div className="mb-4">
                                  <h3 className="font-medium text-gray-900 mb-2">Your Answer:</h3>
                                  <p className="text-gray-700 leading-relaxed bg-gray-50 p-3 rounded">
                                    {correspondingAnswer.content}
                                  </p>
                                </div>
                              )}
                              
                              <div>
                                <h3 className="font-medium text-gray-900 mb-2">Feedback:</h3>
                                <p className="text-gray-700 leading-relaxed">
                                  {message.content}
                                </p>
                              </div>
                            </div>
                          );
                        })}
                    </div>
                  </div>

                  {/* Learning Roadmap */}
                  {chatHistory.messages.some(msg => msg.type === 'roadmap') && (
                    <div>
                      <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
                        <svg className="w-6 h-6 mr-2 text-purple-600" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M12 7a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0V8.414l-4.293 4.293a1 1 0 01-1.414 0L8 10.414l-4.293 4.293a1 1 0 01-1.414-1.414l5-5a1 1 0 011.414 0L11 10.586 14.586 7H12z" clipRule="evenodd" />
                        </svg>
                        Personalized Learning Roadmap
                      </h2>
                      
                      <div className="bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200 rounded-lg p-6">
                        <div className="roadmap-content prose prose-lg max-w-none">
                          {chatHistory.messages
                            .filter(msg => msg.type === 'roadmap')
                            .map((message, index) => (
                              <div key={index}>
                                <div 
                                  dangerouslySetInnerHTML={{ 
                                    __html: message.content
                                      .replace(/\n/g, '<br/>')
                                      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                                      .replace(/\*(.*?)\*/g, '<em>$1</em>')
                                      .replace(/#{1,6}\s*(.*)/g, '<h3 class="text-lg font-semibold text-gray-900 mt-4 mb-2">$1</h3>')
                                  }}
                                />
                              </div>
                            ))}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-8">
                  <svg className="w-12 h-12 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
                  </svg>
                  <p className="text-gray-500">No results found for this session</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </>
    );
  };

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-lg text-gray-600">Please log in to view your dashboard.</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="flex">
        {/* Main Content */}
        <div className={`flex-1 transition-all duration-300 ${sidebarOpen ? 'lg:mr-2/3' : ''}`}>
          <div className="py-8">
            <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="mb-8">
                <h1 className="text-3xl font-bold text-gray-900">Interview Dashboard</h1>
                <p className="mt-2 text-gray-600">
                  Welcome back, {user.full_name}! Here's your interview history and performance.
                </p>
              </div>

              {error && (
                <div className="mb-6 p-4 bg-red-50 border-l-4 border-red-400 text-red-700">
                  {error}
                </div>
              )}

              {isLoading && !sidebarOpen && (
                <div className="text-center py-8">
                  <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                  <p className="mt-2 text-gray-600">Loading...</p>
                </div>
              )}

              {renderAnalytics()}
              {renderSessionsList()}
            </div>
          </div>
        </div>

        {/* Chat Sidebar */}
        {renderChatSidebar()}
      </div>
    </div>
  );
};

export default InterviewDashboard;
