import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Clock, CheckCircle, ArrowRight, Brain, Volume2, Mic, Square, Play, RotateCcw } from 'lucide-react';
import VoiceRecorder from './VoiceRecorder';

const Interview = ({ interviewData, onSessionCreated }) => {
  const navigate = useNavigate();
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState(Array(interviewData.questions?.length).fill(''));
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [isPlaying, setIsPlaying] = useState(false);
  const audioRef = useRef(null);

  const questions = interviewData.questions || [];

  const handleAnswerChange = (value) => {
    const newAnswers = [...answers];
    newAnswers[currentQuestion] = value;
    setAnswers(newAnswers);
  };

  const handleVoiceRecordingComplete = (transcribedText) => {
    handleAnswerChange(transcribedText);
  };

  const handleRecordingError = (error) => {
    setError(error);
  };
  
  const replayQuestion = () => {
    if (questions.length > 0 && currentQuestion < questions.length) {
      const utterance = new SpeechSynthesisUtterance(questions[currentQuestion]);
      utterance.rate = 1.0;
      utterance.pitch = 1.0;
      window.speechSynthesis.speak(utterance);
    }
  };

  const nextQuestion = () => {
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    }
  };

  const previousQuestion = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1);
    }
  };

  const submitInterview = async () => {
    if (answers.some(answer => !answer.trim())) {
      setError('Please answer all questions before submitting');
      return;
    }

    setIsSubmitting(true);
    setError('');

    try {
      // Get auth token
      const token = localStorage.getItem('token');
      const headers = {
        'Content-Type': 'application/json',
      };
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/interview/submit-answers`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          session_id: interviewData.session_id,
          answers: answers
        })
      });

      if (!response.ok) {
        throw new Error('Failed to submit interview');
      }

      const result = await response.json();
      
      // Pass the complete session data to parent
      onSessionCreated({
        ...interviewData,
        thread_id: interviewData.session_id, // Add thread_id for pin functionality
        answers: answers,
        feedback: result.feedback,
        roadmap: result.roadmap,
        total_score: result.total_score,
        average_score: result.average_score,
        is_pinned: false // Default to not pinned
      });

      navigate('/results');
    } catch (err) {
      setError(err.message || 'Something went wrong');
    } finally {
      setIsSubmitting(false);
    }
  };

  const getProgressPercentage = () => {
    return ((currentQuestion + 1) / questions.length) * 100;
  };

  const getQuestionNumber = (index) => {
    return index + 1;
  };

  const playQuestionAudio = async (questionText) => {
    try {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }

      setIsPlaying(true);
      
      // Create a new audio element
      const audio = new Audio();
      audioRef.current = audio;
      
      // Set up event listeners
      audio.onended = () => {
        setIsPlaying(false);
        audioRef.current = null;
      };
      
      audio.onerror = () => {
        setIsPlaying(false);
        console.error('Error playing audio');
      };
      
      // Call the TTS API
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/tts`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: questionText,
          language: 'en'
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to generate speech');
      }
      
      // Create a blob URL from the response
      const audioBlob = await response.blob();
      const audioUrl = URL.createObjectURL(audioBlob);
      
      // Set the audio source and play
      audio.src = audioUrl;
      await audio.play();
      
    } catch (err) {
      console.error('Error playing question:', err);
      setIsPlaying(false);
    }
  };
  
  // Auto-speak question when it changes
  useEffect(() => {
    if (questions.length > 0 && currentQuestion < questions.length) {
      const speakQuestion = async () => {
        try {
          // Cancel any ongoing speech
          window.speechSynthesis.cancel();
          
          const utterance = new SpeechSynthesisUtterance(questions[currentQuestion]);
          utterance.rate = 1.0;
          utterance.pitch = 1.0;
          
          // Set playing state
          setIsPlaying(true);
          utterance.onend = () => setIsPlaying(false);
          
          window.speechSynthesis.speak(utterance);
        } catch (err) {
          console.error('Error speaking question:', err);
          setIsPlaying(false);
        }
      };
      
      // Small delay to ensure the UI has updated
      const timer = setTimeout(speakQuestion, 500);
      
      // Cleanup function
      return () => {
        clearTimeout(timer);
        window.speechSynthesis.cancel();
        setIsPlaying(false);
      };
    }
  }, [currentQuestion, questions]);

  // Clean up audio on unmount
  useEffect(() => {
    return () => {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
      window.speechSynthesis.cancel();
      setIsPlaying(false);
    };
  }, []);

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">AI Interview</h1>
            <p className="text-gray-600">
              {interviewData.role} at {interviewData.company}
            </p>
          </div>
          <div className="flex items-center space-x-2 text-sm text-gray-500">
            <Clock className="h-4 w-4" />
            <span>Question {currentQuestion + 1} of {questions.length}</span>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-primary-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${getProgressPercentage()}%` }}
          ></div>
        </div>
      </div>

      {/* Question Card */}
      <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
        <div className="mb-6">
          <div className="flex items-center space-x-3 mb-4">
            <div className="bg-primary-100 rounded-full p-2">
              <Brain className="h-6 w-6 text-primary-600" />
            </div>
            <span className="text-sm font-medium text-primary-600">
              Question {getQuestionNumber(currentQuestion)}
            </span>
          </div>
          <div className="flex items-center">
            <h2 className="text-xl font-semibold text-gray-900 leading-relaxed flex-1">
              {questions[currentQuestion]}
            </h2>
            <button
              onClick={() => playQuestionAudio(questions[currentQuestion])}
              disabled={isPlaying}
              className="ml-4 p-2 text-gray-500 hover:text-primary-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              aria-label="Play question audio"
            >
              <Volume2 className={`h-6 w-6 ${isPlaying ? 'text-primary-600' : ''}`} />
            </button>
          </div>
        </div>

        {/* Answer Input */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Your Answer
          </label>
          <div className="space-y-6">
            {/* Question replay button */}
            <div className="flex justify-center">
              <button
                onClick={replayQuestion}
                className="flex items-center px-4 py-2 text-sm font-medium text-blue-600 bg-blue-100 rounded-lg hover:bg-blue-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
                title="Replay question"
              >
                <Play className="w-4 h-4 mr-2" />
                Replay Question
              </button>
            </div>
            
            {/* Voice recording section */}
            <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
              <h3 className="text-sm font-medium text-gray-700 mb-3">Your Answer</h3>
              <VoiceRecorder
                key={`recorder-${currentQuestion}`}
                questionIndex={currentQuestion}
                onRecordingComplete={handleVoiceRecordingComplete}
                onError={handleRecordingError}
                buttonText={answers[currentQuestion] ? 'Re-record Answer' : 'Record Answer'}
              />
              
              {/* Show transcribed answer */}
              {answers[currentQuestion] && (
                <div className="mt-4 p-3 bg-white border border-gray-200 rounded-lg">
                  <p className="text-sm text-gray-600 mb-2">Your transcribed answer:</p>
                  <p className="text-gray-800">{answers[currentQuestion]}</p>
                </div>
              )}
            </div>
            
            {/* Navigation buttons */}
            <div className="flex justify-between pt-2">
              <button
                onClick={previousQuestion}
                disabled={currentQuestion === 0}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500 disabled:opacity-50"
              >
                Previous
              </button>
              
              {currentQuestion < questions.length - 1 ? (
                <button
                  onClick={nextQuestion}
                  disabled={!answers[currentQuestion]}
                  className="flex items-center px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
                >
                  Next Question <ArrowRight className="ml-2 w-4 h-4" />
                </button>
              ) : (
                <button
                  onClick={submitInterview}
                  disabled={!answers[currentQuestion] || isSubmitting}
                  className="flex items-center px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-lg hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 disabled:opacity-50"
                >
                  {isSubmitting ? 'Submitting...' : 'Submit Interview'}
                  {!isSubmitting && <CheckCircle className="ml-2 w-4 h-4" />}
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Navigation */}
        <div className="flex items-center justify-between">
          <button
            onClick={previousQuestion}
            disabled={currentQuestion === 0}
            className="flex items-center space-x-2 px-4 py-2 text-gray-600 hover:text-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <ArrowRight className="h-4 w-4 rotate-180" />
            <span>Previous</span>
          </button>

          <div className="flex items-center space-x-4">
            {currentQuestion < questions.length - 1 ? (
              <button
                onClick={nextQuestion}
                disabled={!answers[currentQuestion].trim()}
                className="flex items-center space-x-2 px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <span>Next</span>
                <ArrowRight className="h-4 w-4" />
              </button>
            ) : (
              <button
                onClick={submitInterview}
                disabled={isSubmitting || answers.some(answer => !answer.trim())}
                className="flex items-center space-x-2 px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isSubmitting ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    <span>Submitting...</span>
                  </>
                ) : (
                  <>
                    <CheckCircle className="h-4 w-4" />
                    <span>Submit Interview</span>
                  </>
                )}
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Question Navigation */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Question Navigation</h3>
        <div className="grid grid-cols-3 gap-4">
          {questions.map((_, index) => (
            <button
              key={index}
              onClick={() => setCurrentQuestion(index)}
              className={`p-4 rounded-lg border-2 transition-all ${
                index === currentQuestion
                  ? 'border-primary-500 bg-primary-50 text-primary-700'
                  : answers[index].trim()
                  ? 'border-green-300 bg-green-50 text-green-700'
                  : 'border-gray-200 bg-gray-50 text-gray-500 hover:border-gray-300'
              }`}
            >
              <div className="text-center">
                <div className="text-lg font-semibold">{index + 1}</div>
                <div className="text-xs">
                  {answers[index].trim() ? 'Answered' : 'Pending'}
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="fixed bottom-4 right-4 bg-red-50 border border-red-200 rounded-lg p-4 max-w-md">
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}
    </div>
  );
};

export default Interview;