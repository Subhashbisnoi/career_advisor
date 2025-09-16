import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Clock, Calendar, Star, User, MessageCircle, TrendingUp, FileText, Award, Target } from 'lucide-react';

// Component to format roadmap content from markdown to styled HTML
const FormattedRoadmap = ({ content }) => {
  const formatRoadmapContent = (text) => {
    if (!text) return '';
    
    // Split by lines for processing
    const lines = text.split('\n');
    const formattedLines = [];
    let inList = false;
    
    lines.forEach((line, index) => {
      const trimmedLine = line.trim();
      
      if (trimmedLine.startsWith('# ')) {
        // Main heading
        const text = trimmedLine.replace('# ', '');
        formattedLines.push(`<h2 class="text-xl font-bold text-gray-900 mb-4 mt-6">${text}</h2>`);
      } else if (trimmedLine.startsWith('## ')) {
        // Section heading
        const text = trimmedLine.replace('## ', '');
        formattedLines.push(`<h3 class="text-lg font-semibold text-gray-800 mb-3 mt-5">${text}</h3>`);
      } else if (trimmedLine.startsWith('### ')) {
        // Subsection heading
        const text = trimmedLine.replace('### ', '');
        formattedLines.push(`<h4 class="text-md font-medium text-gray-700 mb-2 mt-4">${text}</h4>`);
      } else if (trimmedLine.startsWith('- ') || trimmedLine.startsWith('* ')) {
        // List items
        if (!inList) {
          formattedLines.push('<ul class="list-disc pl-6 mb-3 space-y-1">');
          inList = true;
        }
        const text = trimmedLine.replace(/^[-*] /, '');
        // Handle nested formatting like **bold**
        const formattedText = text
          .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
          .replace(/\*(.*?)\*/g, '<em>$1</em>')
          .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" class="text-blue-600 hover:text-blue-800 underline" target="_blank" rel="noopener noreferrer">$1</a>');
        formattedLines.push(`<li class="text-gray-700">${formattedText}</li>`);
      } else if (trimmedLine.startsWith('---')) {
        // Horizontal rule
        if (inList) {
          formattedLines.push('</ul>');
          inList = false;
        }
        formattedLines.push('<hr class="my-6 border-gray-300">');
      } else if (trimmedLine === '') {
        // Empty line - close list if open and add spacing
        if (inList) {
          formattedLines.push('</ul>');
          inList = false;
        } else {
          formattedLines.push('<div class="mb-2"></div>');
        }
      } else if (trimmedLine.length > 0) {
        // Regular paragraph
        if (inList) {
          formattedLines.push('</ul>');
          inList = false;
        }
        // Handle nested formatting
        const formattedText = trimmedLine
          .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
          .replace(/\*(.*?)\*/g, '<em>$1</em>')
          .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" class="text-blue-600 hover:text-blue-800 underline" target="_blank" rel="noopener noreferrer">$1</a>');
        formattedLines.push(`<p class="text-gray-700 mb-3 leading-relaxed">${formattedText}</p>`);
      }
    });
    
    // Close any open list
    if (inList) {
      formattedLines.push('</ul>');
    }
    
    return formattedLines.join('');
  };

  return (
    <div 
      className="roadmap-content"
      dangerouslySetInnerHTML={{ __html: formatRoadmapContent(content) }}
    />
  );
};

const ChatHistory = () => {
  const { user } = useAuth();
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedSession, setSelectedSession] = useState(null);

  useEffect(() => {
    if (user) {
      fetchChatHistory();
    }
  }, [user]);

  const fetchChatHistory = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(
        `${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/interview/sessions`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (!response.ok) {
        throw new Error('Failed to fetch chat history');
      }

      const data = await response.json();
      setSessions(data.sessions || []);
    } catch (err) {
      setError(err.message || 'Failed to load chat history');
      console.error('Error fetching chat history:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'in_progress':
        return 'bg-blue-100 text-blue-800';
      case 'paused':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getScoreColor = (score) => {
    if (score >= 8) return 'text-green-600';
    if (score >= 6) return 'text-yellow-600';
    return 'text-red-600';
  };

  const handleViewDetails = async (session) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(
        `${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/interview/session/${session.session_id}/chat`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (!response.ok) {
        throw new Error('Failed to fetch session details');
      }

      const details = await response.json();
      setSelectedSession({ ...session, details: details.messages });
    } catch (err) {
      console.error('Error fetching session details:', err);
      setError('Failed to load session details');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="bg-red-50 border-l-4 border-red-400 p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-red-700">{error}</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Interview History</h1>
        <p className="text-gray-600">View all your previous interview sessions and performance</p>
      </div>

      {sessions.length === 0 ? (
        <div className="text-center py-12">
          <MessageCircle className="mx-auto h-12 w-12 text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No interview sessions yet</h3>
          <p className="text-gray-600 mb-6">Start your first interview to see your history here</p>
          <button
            onClick={() => window.location.href = '/'}
            className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700"
          >
            Start Interview
          </button>
        </div>
      ) : (
        <div className="grid gap-6">
          {sessions.map((session) => (
            <div key={session.id} className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-3">
                    <h3 className="text-lg font-semibold text-gray-900">
                      {session.role || 'Interview Session'}
                    </h3>
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(session.status)}`}>
                      {session.status || 'Unknown'}
                    </span>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <Calendar className="h-4 w-4" />
                      <span>{formatDate(session.created_at)}</span>
                    </div>
                    
                    {session.company && (
                      <div className="flex items-center gap-2 text-sm text-gray-600">
                        <User className="h-4 w-4" />
                        <span>{session.company}</span>
                      </div>
                    )}
                    
                    {session.average_score && (
                      <div className="flex items-center gap-2 text-sm">
                        <Star className="h-4 w-4 text-yellow-500" />
                        <span className={`font-medium ${getScoreColor(session.average_score)}`}>
                          {session.average_score}/10
                        </span>
                      </div>
                    )}
                  </div>

                  {session.duration && (
                    <div className="flex items-center gap-2 text-sm text-gray-600 mb-4">
                      <Clock className="h-4 w-4" />
                      <span>{Math.round(session.duration / 60)} minutes</span>
                    </div>
                  )}

                  {session.total_questions && (
                    <div className="text-sm text-gray-600 mb-4">
                      <span className="font-medium">{session.answered_questions || 0}</span> of{' '}
                      <span className="font-medium">{session.total_questions}</span> questions answered
                      <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
                        <div
                          className="bg-indigo-600 h-2 rounded-full"
                          style={{
                            width: `${((session.answered_questions || 0) / session.total_questions) * 100}%`
                          }}
                        ></div>
                      </div>
                    </div>
                  )}
                </div>

                <div className="flex flex-col gap-2 ml-4">
                  <button
                    onClick={() => handleViewDetails(session)}
                    className="inline-flex items-center px-3 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                  >
                    <TrendingUp className="h-3 w-3 mr-1" />
                    View Details
                  </button>
                  
                  {session.feedback_available && (
                    <button
                      onClick={() => window.location.href = `/results?session=${session.id}`}
                      className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded text-indigo-700 bg-indigo-100 hover:bg-indigo-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                    >
                      View Report
                    </button>
                  )}
                </div>
              </div>

              {session.key_topics && session.key_topics.length > 0 && (
                <div className="mt-4 pt-4 border-t border-gray-200">
                  <p className="text-sm font-medium text-gray-700 mb-2">Topics Covered:</p>
                  <div className="flex flex-wrap gap-2">
                    {session.key_topics.slice(0, 5).map((topic, index) => (
                      <span
                        key={index}
                        className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800"
                      >
                        {topic}
                      </span>
                    ))}
                    {session.key_topics.length > 5 && (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                        +{session.key_topics.length - 5} more
                      </span>
                    )}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Session Details Modal */}
      {selectedSession && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center p-6 border-b">
              <div>
                <h2 className="text-xl font-bold text-gray-900">Interview Session Details</h2>
                <p className="text-sm text-gray-600 mt-1">
                  {selectedSession.role} at {selectedSession.company}
                </p>
              </div>
              <button
                onClick={() => setSelectedSession(null)}
                className="text-gray-400 hover:text-gray-600 text-2xl font-bold"
              >
                ×
              </button>
            </div>
            
            <div className="p-6">
              {selectedSession.details && selectedSession.details.length > 0 ? (
                <div className="space-y-6">
                  {/* Session Overview */}
                  <div className="bg-gray-50 rounded-lg p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <div className="flex items-center text-sm text-gray-600">
                          <Calendar className="h-4 w-4 mr-1" />
                          {formatDate(selectedSession.created_at)}
                        </div>
                        <div className="flex items-center text-sm text-gray-600">
                          <Clock className="h-4 w-4 mr-1" />
                          {selectedSession.status}
                        </div>
                      </div>
                      {selectedSession.score && (
                        <div className="flex items-center">
                          <Star className="h-4 w-4 mr-1 text-yellow-500" />
                          <span className={`font-medium ${getScoreColor(selectedSession.score)}`}>
                            {selectedSession.score}/10
                          </span>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Interview Content */}
                  {(() => {
                    const questions = selectedSession.details.filter(msg => msg.type === 'question');
                    const answers = selectedSession.details.filter(msg => msg.type === 'answer');
                    const feedback = selectedSession.details.filter(msg => msg.type === 'feedback');
                    const roadmap = selectedSession.details.find(msg => msg.type === 'roadmap');

                    return (
                      <div className="space-y-6">
                        {/* Questions and Answers */}
                        {questions.length > 0 && (
                          <div>
                            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                              <MessageCircle className="h-5 w-5 mr-2" />
                              Interview Questions & Answers
                            </h3>
                            <div className="space-y-4">
                              {questions.map((question, index) => {
                                const answer = answers.find(a => a.question_number === question.question_number);
                                const feedbackItem = feedback.find(f => f.question_number === question.question_number);
                                
                                return (
                                  <div key={index} className="border rounded-lg p-4 bg-white">
                                    <div className="space-y-3">
                                      {/* Question */}
                                      <div>
                                        <div className="flex items-center mb-2">
                                          <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-blue-100 text-blue-800 text-sm font-medium mr-2">
                                            Q{question.question_number}
                                          </span>
                                          <span className="text-sm font-medium text-gray-700">Question</span>
                                        </div>
                                        <p className="text-gray-800 ml-8">{question.content}</p>
                                      </div>
                                      
                                      {/* Answer */}
                                      {answer && (
                                        <div>
                                          <div className="flex items-center mb-2">
                                            <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-green-100 text-green-800 text-sm font-medium mr-2">
                                              A{answer.question_number}
                                            </span>
                                            <span className="text-sm font-medium text-gray-700">Your Answer</span>
                                          </div>
                                          <p className="text-gray-800 ml-8 bg-gray-50 p-3 rounded">{answer.content}</p>
                                        </div>
                                      )}
                                      
                                      {/* Feedback */}
                                      {feedbackItem && (
                                        <div>
                                          <div className="flex items-center justify-between mb-2">
                                            <div className="flex items-center">
                                              <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-orange-100 text-orange-800 text-sm font-medium mr-2">
                                                F{feedbackItem.question_number}
                                              </span>
                                              <span className="text-sm font-medium text-gray-700">Feedback</span>
                                            </div>
                                            {feedbackItem.marks && (
                                              <div className="flex items-center">
                                                <Award className="h-4 w-4 mr-1 text-yellow-500" />
                                                <span className={`font-medium ${getScoreColor(feedbackItem.marks)}`}>
                                                  {feedbackItem.marks}/10
                                                </span>
                                              </div>
                                            )}
                                          </div>
                                          <p className="text-gray-800 ml-8 bg-orange-50 p-3 rounded">{feedbackItem.content}</p>
                                        </div>
                                      )}
                                    </div>
                                  </div>
                                );
                              })}
                            </div>
                          </div>
                        )}

                        {/* Roadmap */}
                        {roadmap && (
                          <div>
                            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                              <Target className="h-5 w-5 mr-2" />
                              Personalized Learning Roadmap
                            </h3>
                            <div className="border rounded-lg p-4 bg-blue-50">
                              <div className="prose prose-sm max-w-none">
                                <FormattedRoadmap content={roadmap.content} />
                              </div>
                            </div>
                          </div>
                        )}
                      </div>
                    );
                  })()}
                </div>
              ) : (
                <div className="text-center py-8">
                  <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600">No detailed information available for this session.</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatHistory;
