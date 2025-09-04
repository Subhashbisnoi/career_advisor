import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { 
  startInterviewSession, 
  submitAnswer, 
  getChatHistory, 
  getSessionStatus,
  uploadResume,
  formatChatHistory,
  calculateProgress,
  getStatusColor,
  formatScore
} from '../../services/interviewV2';

const InterviewV2 = () => {
  const { user } = useAuth();
  const [currentSession, setCurrentSession] = useState(null);
  const [chatHistory, setChatHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  
  // Interview setup state
  const [role, setRole] = useState('');
  const [company, setCompany] = useState('');
  const [resumeFile, setResumeFile] = useState(null);
  const [resumeText, setResumeText] = useState('');
  const [isSetupMode, setIsSetupMode] = useState(true);
  
  // Interview progress state
  const [currentAnswer, setCurrentAnswer] = useState('');
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [questions, setQuestions] = useState([]);
  const [sessionStatus, setSessionStatus] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Handle resume upload
  const handleResumeUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setError('Please upload a PDF file');
      return;
    }

    setResumeFile(file);
    setIsLoading(true);
    setError('');

    try {
      const result = await uploadResume(file);
      setResumeText(result.resume_text);
    } catch (err) {
      setError(err.message || 'Failed to upload resume');
    } finally {
      setIsLoading(false);
    }
  };

  // Start interview session
  const handleStartInterview = async () => {
    if (!role.trim() || !company.trim() || !resumeText.trim()) {
      setError('Please fill in all fields and upload a resume');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const result = await startInterviewSession({
        role: role.trim(),
        company: company.trim(),
        resume_text: resumeText
      });

      setCurrentSession(result);
      setQuestions(result.questions || []);
      setIsSetupMode(false);
      setCurrentQuestionIndex(0);
      setSidebarOpen(true); // Open sidebar when interview starts
      
      // Load initial chat history
      await loadChatHistory(result.thread_id);
      
    } catch (err) {
      setError(err.message || 'Failed to start interview');
    } finally {
      setIsLoading(false);
    }
  };

  // Submit answer
  const handleSubmitAnswer = async () => {
    if (!currentAnswer.trim()) {
      setError('Please provide an answer');
      return;
    }

    if (!currentSession) {
      setError('No active session');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const result = await submitAnswer(
        currentSession.thread_id,
        currentQuestionIndex + 1,
        currentAnswer.trim()
      );

      setCurrentAnswer('');
      
      // Reload chat history to get feedback
      await loadChatHistory(currentSession.thread_id);
      
      // Update session status
      await loadSessionStatus(currentSession.thread_id);
      
      // Move to next question if available
      if (currentQuestionIndex < questions.length - 1) {
        setCurrentQuestionIndex(currentQuestionIndex + 1);
      }
      
    } catch (err) {
      setError(err.message || 'Failed to submit answer');
    } finally {
      setIsLoading(false);
    }
  };

  // Load chat history
  const loadChatHistory = async (threadId) => {
    try {
      const history = await getChatHistory(threadId);
      const formattedHistory = formatChatHistory(history);
      setChatHistory(formattedHistory);
    } catch (err) {
      console.error('Failed to load chat history:', err);
    }
  };

  // Load session status
  const loadSessionStatus = async (threadId) => {
    try {
      const status = await getSessionStatus(threadId);
      setSessionStatus(status);
    } catch (err) {
      console.error('Failed to load session status:', err);
    }
  };

  // Reset to start new interview
  const handleNewInterview = () => {
    setCurrentSession(null);
    setChatHistory([]);
    setRole('');
    setCompany('');
    setResumeFile(null);
    setResumeText('');
    setIsSetupMode(true);
    setCurrentAnswer('');
    setCurrentQuestionIndex(0);
    setQuestions([]);
    setSessionStatus(null);
    setError('');
    setSidebarOpen(false);
  };

  // Render setup form
  const renderSetupForm = () => (
    <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-lg">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Start New Interview</h2>
      
      {error && (
        <div className="mb-4 p-4 bg-red-50 border-l-4 border-red-400 text-red-700">
          {error}
        </div>
      )}

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Job Role *
          </label>
          <input
            type="text"
            value={role}
            onChange={(e) => setRole(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="e.g., Software Engineer, Data Scientist"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Company *
          </label>
          <input
            type="text"
            value={company}
            onChange={(e) => setCompany(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="e.g., Google, Microsoft, Startup Inc."
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Resume (PDF) *
          </label>
          <input
            type="file"
            accept=".pdf"
            onChange={handleResumeUpload}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          {resumeText && (
            <p className="mt-2 text-sm text-green-600">
              ✓ Resume uploaded and processed successfully
            </p>
          )}
        </div>

        <button
          onClick={handleStartInterview}
          disabled={isLoading || !role.trim() || !company.trim() || !resumeText.trim()}
          className="w-full py-2 px-4 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? 'Starting Interview...' : 'Start Interview'}
        </button>
      </div>
    </div>
  );

  // Render chat sidebar
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
          fixed inset-y-0 right-0 w-full max-w-lg bg-white shadow-xl z-50 transform transition-transform duration-300 ease-in-out
          ${sidebarOpen ? 'translate-x-0' : 'translate-x-full'}
          lg:relative lg:translate-x-0 lg:shadow-none lg:z-auto
          ${sidebarOpen ? 'lg:block' : 'lg:hidden'}
        `}>
          <div className="h-full flex flex-col">
            {/* Header */}
            <div className="bg-blue-50 px-4 py-3 border-b border-blue-200">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <svg className="w-5 h-5 text-blue-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                  </svg>
                  <h3 className="text-lg font-semibold text-blue-900">Chat History</h3>
                </div>
                <button
                  onClick={() => setSidebarOpen(false)}
                  className="text-blue-400 hover:text-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded-md p-1 lg:hidden"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>

            {/* Chat Content */}
            <div className="flex-1 overflow-y-auto p-4">
              {chatHistory.length > 0 ? (
                <div className="space-y-3">
                  {chatHistory.map((message, index) => {
                    const isUser = message.role === 'user';
                    const isSystem = message.role === 'system' || message.type === 'system';
                    
                    let bgColor = 'bg-gray-50';
                    let borderColor = 'border-gray-200';
                    
                    if (isUser) {
                      bgColor = 'bg-blue-50';
                      borderColor = 'border-blue-200';
                    } else if (message.type === 'feedback') {
                      bgColor = 'bg-green-50';
                      borderColor = 'border-green-200';
                    } else if (message.type === 'roadmap') {
                      bgColor = 'bg-purple-50';
                      borderColor = 'border-purple-200';
                    }

                    return (
                      <div key={index} className={`border rounded-lg p-3 ${bgColor} ${borderColor}`}>
                        <div className="flex justify-between items-start mb-2">
                          <div className="flex items-center text-xs font-medium text-gray-600">
                            {message.type === 'question' && (
                              <>
                                <svg className="w-3 h-3 mr-1 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
                                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
                                </svg>
                                Q{message.questionNumber}
                              </>
                            )}
                            {message.type === 'answer' && (
                              <>
                                <svg className="w-3 h-3 mr-1 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                </svg>
                                Answer
                              </>
                            )}
                            {message.type === 'feedback' && (
                              <>
                                <svg className="w-3 h-3 mr-1 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                                </svg>
                                Feedback
                              </>
                            )}
                            {message.type === 'roadmap' && (
                              <>
                                <svg className="w-3 h-3 mr-1 text-purple-500" fill="currentColor" viewBox="0 0 20 20">
                                  <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd" />
                                </svg>
                                Roadmap
                              </>
                            )}
                            {isSystem && 'System'}
                          </div>
                          
                          {message.marks !== null && message.marks !== undefined && (
                            <div className="flex items-center text-xs">
                              <svg className="w-3 h-3 text-yellow-500 mr-1" fill="currentColor" viewBox="0 0 20 20">
                                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                              </svg>
                              <span className="font-bold text-gray-700">{message.marks}/10</span>
                            </div>
                          )}
                        </div>

                        <div className="text-sm text-gray-800">
                          {message.type === 'roadmap' ? (
                            <div 
                              className="prose prose-sm max-w-none"
                              dangerouslySetInnerHTML={{ 
                                __html: message.content
                                  .replace(/\n/g, '<br/>')
                                  .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                                  .replace(/\*(.*?)\*/g, '<em>$1</em>')
                              }}
                            />
                          ) : (
                            <p className="whitespace-pre-wrap">{message.content}</p>
                          )}
                        </div>
                        
                        <div className="text-xs text-gray-500 mt-2">
                          {message.timestamp.toLocaleTimeString()}
                        </div>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="text-center py-8">
                  <svg className="w-12 h-12 text-gray-300 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                  </svg>
                  <p className="text-gray-500 text-sm">Chat history will appear here</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </>
    );
  };

  // Render interview interface
  const renderInterview = () => (
    <div className="max-w-4xl mx-auto p-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">
              {currentSession?.role} at {currentSession?.company}
            </h2>
            {sessionStatus && (
              <div className="mt-2 flex items-center space-x-4">
                <span className={`text-sm font-medium ${getStatusColor(sessionStatus.status)}`}>
                  Status: {sessionStatus.status}
                </span>
                {sessionStatus.total_score > 0 && (
                  <span className="text-sm text-gray-600">
                    Score: {formatScore(sessionStatus.total_score)}/30
                  </span>
                )}
              </div>
            )}
          </div>
          <div className="flex items-center space-x-2">
            {!isSetupMode && (
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="px-4 py-2 bg-blue-100 text-blue-700 rounded-md hover:bg-blue-200 transition-colors flex items-center"
              >
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
                Chat History ({chatHistory.length})
              </button>
            )}
            <button
              onClick={handleNewInterview}
              className="px-4 py-2 text-sm bg-gray-600 text-white rounded-md hover:bg-gray-700"
            >
              New Interview
            </button>
          </div>
        </div>

        {/* Progress bar */}
        {sessionStatus && (
          <div className="mt-4">
            <div className="flex justify-between text-sm text-gray-600 mb-1">
              <span>Progress</span>
              <span>{sessionStatus.answers_submitted || 0}/{sessionStatus.total_questions || 3}</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${calculateProgress(sessionStatus)}%` }}
              ></div>
            </div>
          </div>
        )}
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-50 border-l-4 border-red-400 text-red-700">
          {error}
        </div>
      )}

      {/* Chat History */}
      <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Chat History</h3>
        <div className="space-y-4 max-h-96 overflow-y-auto">
          {chatHistory.length > 0 ? (
            chatHistory.map((message, index) => renderMessage(message, index))
          ) : (
            <p className="text-gray-500 text-center">No messages yet</p>
          )}
        </div>
      </div>

      {/* Current Question & Answer */}
      {questions.length > 0 && currentQuestionIndex < questions.length && sessionStatus?.status !== 'completed' && (
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Question {currentQuestionIndex + 1} of {questions.length}
          </h3>
          
          <div className="bg-gray-50 p-4 rounded-lg mb-4">
            <p className="text-gray-800">{questions[currentQuestionIndex]}</p>
          </div>

          <div className="space-y-4">
            <textarea
              value={currentAnswer}
              onChange={(e) => setCurrentAnswer(e.target.value)}
              placeholder="Type your answer here..."
              className="w-full h-32 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            
            <button
              onClick={handleSubmitAnswer}
              disabled={isLoading || !currentAnswer.trim()}
              className="w-full py-2 px-4 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Submitting...' : 'Submit Answer'}
            </button>
          </div>
        </div>
      )}

      {/* Completion Message */}
      {sessionStatus?.status === 'completed' && (
        <div className="bg-green-50 border-l-4 border-green-400 p-4 rounded-lg">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-green-400" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-green-800">Interview Completed!</h3>
              <p className="mt-1 text-sm text-green-700">
                Your final score: {formatScore(sessionStatus.total_score)}/30 
                (Average: {formatScore(sessionStatus.average_score)}/10)
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-lg text-gray-600">Please log in to access the interview.</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Main Content */}
      <div className={`flex-1 transition-all duration-300 ${sidebarOpen ? 'lg:mr-96' : ''}`}>
        <div className="py-8">
          {isSetupMode ? renderSetupForm() : renderInterview()}
        </div>
      </div>

      {/* Chat Sidebar */}
      {!isSetupMode && currentSession && renderChatSidebar()}
    </div>
  );
};

export default InterviewV2;
