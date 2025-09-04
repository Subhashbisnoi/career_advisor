import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, Brain, User, BarChart3, ArrowRight } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import AuthRequiredModal from './auth/AuthRequiredModal';

const Home = ({ onStartInterview }) => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [resumeFile, setResumeFile] = useState(null);
  const [formData, setFormData] = useState({
    role: '',
    company: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [formDataToSubmit, setFormDataToSubmit] = useState(null);

  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0];
      if (file.type === 'application/pdf') {
        setResumeFile(file);
        setError('');
      } else {
        setError('Please upload a PDF file');
      }
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf']
    },
    multiple: false
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!resumeFile) {
      setError('Please upload a resume');
      return;
    }

    if (!formData.role.trim()) {
      setError('Please specify the target role');
      return;
    }

    const interviewData = {
      role: formData.role.trim(),
      company: formData.company.trim(),
      resumeFile
    };

    if (!user) {
      setFormDataToSubmit(interviewData);
      setShowAuthModal(true);
      return;
    }

    // If user is logged in, proceed with the interview
    await startInterview(interviewData);
  };

  const startInterview = async (data) => {
    setIsLoading(true);
    setError('');
    
    try {
      // Create FormData for file upload
      const uploadData = new FormData();
      uploadData.append('file', data.resumeFile);

      // Get auth token if user is logged in
      const token = localStorage.getItem('token');
      const headers = {};
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      // Upload resume and extract text
      const uploadResponse = await fetch(
        `${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/interview/upload-resume`,
        {
          method: 'POST',
          headers,
          body: uploadData
        }
      );

      if (!uploadResponse.ok) {
        const errorData = await uploadResponse.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to process resume');
      }

      const { resume_text } = await uploadResponse.json();
      
      if (!resume_text) {
        throw new Error('Failed to extract text from resume');
      }

      // Start interview with extracted resume text
      const interviewResponse = await fetch(
        `${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/interview/start`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...headers
          },
          body: JSON.stringify({
            role: data.role,
            company: data.company,
            resume_text: resume_text
          })
        }
      );

      if (!interviewResponse.ok) {
        const errorData = await interviewResponse.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to start interview');
      }

      const interviewResult = await interviewResponse.json();

      // Pass data to parent component
      onStartInterview({
        role: data.role,
        company: data.company,
        resume_text: resume_text,
        questions: interviewResult.questions,
        session_id: interviewResult.session_id
      });

      // Navigate to interview page
      navigate('/interview');
    } catch (err) {
      setError(err.message || 'Failed to start interview. Please try again.');
      console.error('Interview error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLoginSuccess = () => {
    if (formDataToSubmit) {
      startInterview(formDataToSubmit);
    }
    setShowAuthModal(false);
  };

  return (
    <div className="max-w-4xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">AI-Powered Interview Preparation</h1>
        <p className="text-xl text-gray-600">Practice with realistic interview questions and get instant feedback</p>
      </div>

      <div className="bg-white shadow rounded-lg p-6 mb-8">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="role" className="block text-sm font-medium text-gray-700 mb-1">
              Target Role
            </label>
            <input
              type="text"
              name="role"
              id="role"
              value={formData.role}
              onChange={handleInputChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
              placeholder="e.g., Software Engineer, Data Scientist"
              required
            />
          </div>

          <div>
            <label htmlFor="company" className="block text-sm font-medium text-gray-700 mb-1">
              Target Company (Optional)
            </label>
            <input
              type="text"
              name="company"
              id="company"
              value={formData.company}
              onChange={handleInputChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
              placeholder="e.g., Google, Microsoft"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Upload Resume (PDF)
            </label>
            <div
              {...getRootProps()}
              className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors ${
                isDragActive ? 'border-indigo-500 bg-indigo-50' : 'border-gray-300 hover:border-indigo-400'
              }`}
            >
              <input {...getInputProps()} />
              {resumeFile ? (
                <div className="space-y-2">
                  <FileText className="mx-auto h-12 w-12 text-green-500" />
                  <p className="text-sm text-green-600 font-medium">
                    {resumeFile.name}
                  </p>
                  <p className="text-xs text-green-500">
                    Click or drag to replace
                  </p>
                </div>
              ) : (
                <div className="space-y-2">
                  <Upload className="h-10 w-10 mx-auto text-gray-400" />
                  <p className="text-sm text-gray-600">
                    {isDragActive ? 'Drop your resume here' : 'Drag and drop your resume here, or click to select'}
                  </p>
                  <p className="text-xs text-gray-500">PDF files only (max 5MB)</p>
                </div>
              )}
            </div>
            {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
          </div>

          <div className="pt-2">
            <button
              type="submit"
              disabled={isLoading}
              className="w-full flex justify-center items-center px-6 py-3 border border-transparent rounded-md shadow-sm text-base font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                'Preparing your interview...'
              ) : (
                <>
                  Start Interview
                  <ArrowRight className="ml-2 h-4 w-4" />
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      <div className="grid md:grid-cols-3 gap-6 mb-12">
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="bg-indigo-100 p-3 rounded-full w-12 h-12 flex items-center justify-center mb-4">
            <Brain className="h-6 w-6 text-indigo-600" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">AI-Powered Questions</h3>
          <p className="text-gray-600">
            Get personalized questions based on your resume and target role
          </p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="bg-indigo-100 p-3 rounded-full w-12 h-12 flex items-center justify-center mb-4">
            <User className="h-6 w-6 text-indigo-600" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Practice Anywhere</h3>
          <p className="text-gray-600">
            Access your interviews anytime, from any device
          </p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="bg-indigo-100 p-3 rounded-full w-12 h-12 flex items-center justify-center mb-4">
            <BarChart3 className="h-6 w-6 text-indigo-600" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Learning Roadmap</h3>
          <p className="text-gray-600">
            Get a personalized plan to improve your skills and interview performance
          </p>
        </div>
      </div>

      <AuthRequiredModal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        onLogin={() => {
          setShowAuthModal(false);
          navigate('/login', { 
            state: { 
              from: { 
                pathname: '/',
                state: { formData: formDataToSubmit }
              } 
            } 
          });
        }}
        onSignup={() => {
          setShowAuthModal(false);
          navigate('/signup', { 
            state: { 
              from: { 
                pathname: '/',
                state: { formData: formDataToSubmit }
              } 
            } 
          });
        }}
      />
    </div>
  );
};

export default Home;
