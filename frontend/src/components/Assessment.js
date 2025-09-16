import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  ChevronLeft, ChevronRight, Brain, Clock, CheckCircle, 
  BarChart3, Target, Users, TrendingUp 
} from 'lucide-react';
import { makeAuthenticatedRequest } from '../services/auth';
import { API_URL } from '../config/api';

const Assessment = ({ assessmentData, onAssessmentCreated, onResultsGenerated }) => {
  const navigate = useNavigate();
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [responses, setResponses] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [questions, setQuestions] = useState([]);
  const [assessmentProgress, setAssessmentProgress] = useState(0);
  const [timeSpent, setTimeSpent] = useState(0);
  const [startTime] = useState(Date.now());

  useEffect(() => {
    // Initialize questions from assessment data
    if (assessmentData && assessmentData.questions) {
      setQuestions(assessmentData.questions);
    }
  }, [assessmentData]);

  useEffect(() => {
    // Update progress
    const progress = questions.length > 0 ? (Object.keys(responses).length / questions.length) * 100 : 0;
    setAssessmentProgress(progress);
  }, [responses, questions]);

  useEffect(() => {
    // Update time spent
    const timer = setInterval(() => {
      setTimeSpent(Math.floor((Date.now() - startTime) / 1000));
    }, 1000);

    return () => clearInterval(timer);
  }, [startTime]);

  const handleResponseChange = (questionId, answer) => {
    setResponses(prev => ({
      ...prev,
      [questionId]: answer
    }));
  };

  const handleNext = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(prev => prev + 1);
    }
  };

  const handlePrevious = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(prev => prev - 1);
    }
  };

  const handleSubmitAssessment = async () => {
    console.log('[FRONTEND DEBUG] Starting assessment submission...');
    console.log('[FRONTEND DEBUG] Assessment data:', assessmentData);
    console.log('[FRONTEND DEBUG] Assessment data keys:', Object.keys(assessmentData || {}));
    console.log('[FRONTEND DEBUG] Thread ID:', assessmentData?.threadId);
    console.log('[FRONTEND DEBUG] Assessment ID:', assessmentData?.assessmentId);
    console.log('[FRONTEND DEBUG] Current responses:', responses);
    
    setIsLoading(true);
    
    try {
      // Format responses for submission
      const formattedResponses = Object.entries(responses).map(([questionId, response]) => ({
        question_id: questionId,
        response: String(response), // Ensure response is a string
        confidence_level: 5 // Default confidence level (1-5)
      }));
      
      // Ensure all required fields are present and of correct type
      if (!formattedResponses.every(r => 
        typeof r.question_id === 'string' && 
        typeof r.response === 'string' && 
        Number.isInteger(r.confidence_level) && 
        r.confidence_level >= 1 && 
        r.confidence_level <= 5
      )) {
        throw new Error('Invalid response format. Please check your answers and try again.');
      }

      console.log('[FRONTEND DEBUG] Formatted responses:', formattedResponses);

      // Submit assessment responses using authenticated request helper
      const submitUrl = `${API_URL}/assessment/submit-responses`;
      console.log('[FRONTEND DEBUG] Submit URL:', submitUrl);
      
      // Create request body matching the backend's expected format
      const requestBody = {
        thread_id: String(assessmentData.threadId), // Use threadId from Home component
        responses: formattedResponses
      };
      
      console.log('[FRONTEND DEBUG] Request body:', JSON.stringify(requestBody, null, 2));
      
      const submitResponse = await makeAuthenticatedRequest(submitUrl, {
        method: 'POST',
        body: JSON.stringify(requestBody)
      });

      console.log('[FRONTEND DEBUG] Submit response status:', submitResponse.status);
      
      if (!submitResponse.ok) {
        const errorData = await submitResponse.json().catch(() => ({}));
        console.error('[FRONTEND DEBUG] Submit error:', errorData);
        throw new Error(errorData.detail || `Failed to submit assessment: ${submitResponse.statusText}`);
      }

      const submitResult = await submitResponse.json();
      console.log('[FRONTEND DEBUG] Submit result:', submitResult);

      // Check if assessment is completed and has an assessment_id
      if (submitResult.status === 'completed' && submitResult.assessment_id) {
        // Generate career recommendations first
        console.log('[FRONTEND DEBUG] Generating career recommendations...');
        
        const recommendationsUrl = `${API_URL}/careers/recommendations`;
        const recommendationsResponse = await makeAuthenticatedRequest(recommendationsUrl, {
          method: 'POST',
          body: JSON.stringify({
            assessment_id: submitResult.assessment_id
          })
        });

        let recommendations = { recommendations: [] };
        if (recommendationsResponse.ok) {
          recommendations = await recommendationsResponse.json();
          console.log('[FRONTEND DEBUG] Career recommendations generated:', recommendations);
        } else {
          const errorData = await recommendationsResponse.json().catch(() => ({}));
          console.warn('[FRONTEND DEBUG] Recommendations generation failed (will retry later):', errorData);
        }
        
        // Get the full results including career recommendations
        console.log('[FRONTEND DEBUG] Getting assessment results...');
        
        const resultsUrl = `${API_URL}/assessment/results/${submitResult.assessment_id}`;
        const resultsResponse = await makeAuthenticatedRequest(resultsUrl, {
          method: 'GET'
        });

        if (resultsResponse.ok) {
          const resultsData = await resultsResponse.json();
          console.log('[FRONTEND DEBUG] Full results received:', resultsData);
          
          // Format results for the Results component
          const formattedResults = {
            assessment_results: resultsData.assessment_results || submitResult,
            career_recommendations: resultsData.career_recommendations || recommendations,
            timeSpent: timeSpent,
            assessmentType: assessmentData.assessmentType,
            generated_at: resultsData.generated_at
          };

          console.log('[FRONTEND DEBUG] Formatted results for Results component:', formattedResults);
          onResultsGenerated(formattedResults);
          navigate('/results');
        } else {
          // Fallback: use basic submit result with generated recommendations
          const fallbackResults = {
            assessment_results: submitResult,
            career_recommendations: recommendations,
            timeSpent: timeSpent,
            assessmentType: assessmentData.assessmentType,
            generated_at: new Date().toISOString()
          };
          
          console.log('[FRONTEND DEBUG] Using fallback results:', fallbackResults);
          onResultsGenerated(fallbackResults);
          navigate('/results');
        }
      } else {
        // For backwards compatibility or if still processing
        console.log('[FRONTEND DEBUG] Assessment still processing, trying career recommendations...');
        
        // Try to generate career recommendations anyway
        const recommendationsUrl = `${API_URL}/careers/recommendations`;
        console.log('[FRONTEND DEBUG] Recommendations URL:', recommendationsUrl);
        
        const recommendationsResponse = await makeAuthenticatedRequest(recommendationsUrl, {
          method: 'POST',
          body: JSON.stringify({
            assessment_id: assessmentData.assessmentId,
            user_background: assessmentData.userBackground || {},
            preferences: {
              industries: [],
              work_environment: '',
              salary_expectations: ''
            }
          })
        });

        console.log('[FRONTEND DEBUG] Recommendations response status:', recommendationsResponse.status);

        let recommendations = { recommendations: [] };
        if (recommendationsResponse.ok) {
          recommendations = await recommendationsResponse.json();
          console.log('[FRONTEND DEBUG] Recommendations result:', recommendations);
        } else {
          const errorData = await recommendationsResponse.json().catch(() => ({}));
          console.warn('[FRONTEND DEBUG] Recommendations error (non-fatal):', errorData);
        }

        // Store results and navigate
        const results = {
          assessment_results: submitResult,
          career_recommendations: recommendations,
          timeSpent: timeSpent,
          assessmentType: assessmentData.assessmentType,
          generated_at: new Date().toISOString()
        };

        console.log('[FRONTEND DEBUG] Final results:', results);
        onResultsGenerated(results);
        navigate('/results');
      }

    } catch (error) {
      console.error('[FRONTEND DEBUG] Assessment submission error:', error);
      alert(`Failed to submit assessment: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const currentQuestion = questions[currentQuestionIndex];
  const isCurrentQuestionAnswered = currentQuestion && responses[currentQuestion.id];
  const allQuestionsAnswered = questions.every(q => responses[q.id]);

  if (!assessmentData || questions.length === 0) {
    return (
      <div className="max-w-4xl mx-auto py-12 px-4">
        <div className="bg-white rounded-xl shadow-lg p-8 text-center">
          <Brain className="h-16 w-16 text-indigo-600 mx-auto mb-4 animate-pulse" />
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Loading Your Assessment</h2>
          <p className="text-gray-600">Please wait while we prepare your personalized career assessment...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto py-8 px-4">
      {/* Assessment Header */}
      <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
        <div className="flex justify-between items-center mb-4">
          <h1 className="text-2xl font-bold text-gray-900">Career Assessment</h1>
          <div className="flex items-center space-x-4">
            <div className="flex items-center text-gray-600">
              <Clock className="h-5 w-5 mr-2" />
              <span>{formatTime(timeSpent)}</span>
            </div>
            <div className="text-sm text-gray-500">
              Question {currentQuestionIndex + 1} of {questions.length}
            </div>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="w-full bg-gray-200 rounded-full h-2 mb-4">
          <div
            className="bg-indigo-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${((currentQuestionIndex + 1) / questions.length) * 100}%` }}
          ></div>
        </div>

        {/* Assessment Type Indicator */}
        <div className="flex items-center justify-center space-x-6 text-sm">
          <div className={`flex items-center ${assessmentData.assessmentType === 'skills' ? 'text-indigo-600' : 'text-gray-400'}`}>
            <BarChart3 className="h-4 w-4 mr-1" />
            <span>Skills</span>
          </div>
          <div className={`flex items-center ${assessmentData.assessmentType === 'comprehensive' ? 'text-indigo-600' : 'text-gray-400'}`}>
            <Brain className="h-4 w-4 mr-1" />
            <span>Comprehensive</span>
          </div>
          <div className={`flex items-center ${assessmentData.assessmentType === 'interest' ? 'text-indigo-600' : 'text-gray-400'}`}>
            <Target className="h-4 w-4 mr-1" />
            <span>Interests</span>
          </div>
        </div>
      </div>

      {/* Question Card */}
      <div className="bg-white rounded-xl shadow-lg p-8 mb-6">
        <div className="mb-6">
          <div className="flex items-start justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900 flex-1">
              {currentQuestion.question}
            </h2>
            {isCurrentQuestionAnswered && (
              <CheckCircle className="h-6 w-6 text-green-500 ml-4 flex-shrink-0" />
            )}
          </div>
          
          {currentQuestion.description && (
            <p className="text-gray-600 mb-6">{currentQuestion.description}</p>
          )}
        </div>

        {/* Question Options */}
        <div className="space-y-3">
          {currentQuestion.type === 'multiple_choice' && currentQuestion.options?.map((option, index) => (
            <div
              key={index}
              className={`border-2 rounded-lg p-4 cursor-pointer transition-all ${
                responses[currentQuestion.id] === option.value
                  ? 'border-indigo-500 bg-indigo-50'
                  : 'border-gray-200 hover:border-indigo-300'
              }`}
              onClick={() => handleResponseChange(currentQuestion.id, option.value)}
            >
              <div className="flex items-center">
                <div className={`w-4 h-4 rounded-full border-2 mr-3 ${
                  responses[currentQuestion.id] === option.value
                    ? 'border-indigo-500 bg-indigo-500'
                    : 'border-gray-300'
                }`}>
                  {responses[currentQuestion.id] === option.value && (
                    <div className="w-2 h-2 bg-white rounded-full m-0.5"></div>
                  )}
                </div>
                <div>
                  <div className="font-medium text-gray-900">{option.label}</div>
                  {option.description && (
                    <div className="text-sm text-gray-600 mt-1">{option.description}</div>
                  )}
                </div>
              </div>
            </div>
          ))}

          {/* Text Input for Open Questions and Scenario Questions */}
          {(currentQuestion.type === 'text' || currentQuestion.type === 'scenario') && (
            <div className="space-y-4">
              {currentQuestion.type === 'scenario' && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
                  <h4 className="font-semibold text-blue-900 mb-2">Scenario:</h4>
                  <p className="text-blue-800">{currentQuestion.scenario}</p>
                </div>
              )}
              <textarea
                value={responses[currentQuestion.id] || ''}
                onChange={(e) => handleResponseChange(currentQuestion.id, e.target.value)}
                placeholder={
                  currentQuestion.type === 'scenario' 
                    ? "Describe how you would handle this situation..."
                    : "Type your answer here..."
                }
                className="w-full p-4 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500"
                rows="4"
              />
            </div>
          )}

          {/* Scale Input */}
          {currentQuestion.type === 'scale' && (
            <div className="space-y-4">
              <div className="flex justify-between text-sm text-gray-600">
                <span>{currentQuestion.scale_labels?.min || 'Strongly Disagree'}</span>
                <span>{currentQuestion.scale_labels?.max || 'Strongly Agree'}</span>
              </div>
              <div className="flex justify-center space-x-4">
                {[1, 2, 3, 4, 5].map((value) => (
                  <button
                    key={value}
                    onClick={() => handleResponseChange(currentQuestion.id, value)}
                    className={`w-12 h-12 rounded-full font-semibold transition-all ${
                      responses[currentQuestion.id] === value
                        ? 'bg-indigo-600 text-white'
                        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                    }`}
                  >
                    {value}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Navigation */}
      <div className="flex justify-between items-center">
        <button
          onClick={handlePrevious}
          disabled={currentQuestionIndex === 0}
          className="flex items-center px-6 py-3 text-gray-600 bg-gray-100 rounded-lg hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <ChevronLeft className="h-5 w-5 mr-2" />
          Previous
        </button>

        <div className="flex items-center space-x-4">
          <div className="text-sm text-gray-500">
            {Object.keys(responses).length} of {questions.length} answered
          </div>
          <div className="w-24 bg-gray-200 rounded-full h-2">
            <div
              className="bg-green-500 h-2 rounded-full transition-all duration-300"
              style={{ width: `${assessmentProgress}%` }}
            ></div>
          </div>
        </div>

        {currentQuestionIndex === questions.length - 1 ? (
          <button
            onClick={handleSubmitAssessment}
            disabled={!allQuestionsAnswered || isLoading}
            className="flex items-center px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isLoading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Analyzing...
              </>
            ) : (
              <>
                Complete Assessment
                <CheckCircle className="h-5 w-5 ml-2" />
              </>
            )}
          </button>
        ) : (
          <button
            onClick={handleNext}
            disabled={!isCurrentQuestionAnswered}
            className="flex items-center px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Next
            <ChevronRight className="h-5 w-5 ml-2" />
          </button>
        )}
      </div>
    </div>
  );
};

export default Assessment;
