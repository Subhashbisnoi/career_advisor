import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, Building, User, Play, ArrowRight, Brain, BarChart3 } from 'lucide-react';

const Home = ({ onStartInterview }) => {
  const navigate = useNavigate();
  const [resumeFile, setResumeFile] = useState(null);
  const [formData, setFormData] = useState({
    role: '',
    company: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

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
    
    if (!formData.role.trim() || !formData.company.trim()) {
      setError('Please fill in all fields');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      // Create FormData for file upload
      const uploadData = new FormData();
      uploadData.append('file', resumeFile);

      // Upload resume and extract text
      const uploadResponse = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/interview/upload-resume`, {
        method: 'POST',
        body: uploadData
      });

      if (!uploadResponse.ok) {
        const errorData = await uploadResponse.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to process resume');
      }

      const { resume_text } = await uploadResponse.json();
      
      if (!resume_text) {
        throw new Error('Failed to extract text from resume');
      }

      // Start interview with extracted resume text
      const interviewResponse = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/interview/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          role: formData.role,
          company: formData.company,
          resume_text: resume_text
        })
      });

      if (!interviewResponse.ok) {
        const errorData = await interviewResponse.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to start interview');
      }

      const interviewResult = await interviewResponse.json();

      // Pass data to parent component and navigate
      onStartInterview({
        ...formData,
        resume_text: resume_text,
        questions: interviewResult.questions,
        session_id: interviewResult.session_id
      });

      navigate('/interview');
    } catch (err) {
      setError(err.message || 'Something went wrong');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          AI-Powered Interview Practice
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          Upload your resume, set your target role, and practice with AI-generated questions. 
          Get instant feedback and a personalized learning roadmap.
        </p>
      </div>

      <div className="bg-white rounded-lg shadow-lg p-8">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Resume Upload */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Upload Your Resume (PDF)
            </label>
            <div
              {...getRootProps()}
              className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
                isDragActive
                  ? 'border-primary-500 bg-primary-50'
                  : resumeFile
                  ? 'border-green-500 bg-green-50'
                  : 'border-gray-300 hover:border-primary-400 hover:bg-gray-50'
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
                  <Upload className="mx-auto h-12 w-12 text-gray-400" />
                  <p className="text-sm text-gray-600">
                    {isDragActive
                      ? 'Drop the PDF here'
                      : 'Drag and drop a PDF file, or click to select'}
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Role and Company Inputs */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label htmlFor="role" className="block text-sm font-medium text-gray-700 mb-2">
                Target Role
              </label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <input
                  type="text"
                  id="role"
                  name="role"
                  value={formData.role}
                  onChange={handleInputChange}
                  placeholder="e.g., Software Engineer, Data Scientist"
                  className="pl-10 w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  required
                />
              </div>
            </div>

            <div>
              <label htmlFor="company" className="block text-sm font-medium text-gray-700 mb-2">
                Target Company
              </label>
              <div className="relative">
                <Building className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <input
                  type="text"
                  id="company"
                  name="company"
                  value={formData.company}
                  onChange={handleInputChange}
                  placeholder="e.g., Google, Microsoft"
                  className="pl-10 w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  required
                />
              </div>
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-md p-4">
              <p className="text-sm text-red-600">{error}</p>
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-primary-600 text-white py-3 px-6 rounded-md font-medium hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center space-x-2"
          >
            {isLoading ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                <span>Starting Interview...</span>
              </>
            ) : (
              <>
                <Play className="h-5 w-5" />
                <span>Start Interview</span>
                <ArrowRight className="h-5 w-5" />
              </>
            )}
          </button>
        </form>
      </div>

      {/* Features */}
      <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="text-center">
          <div className="bg-primary-100 rounded-full p-4 w-16 h-16 mx-auto mb-4 flex items-center justify-center">
            <Brain className="h-8 w-8 text-primary-600" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">AI-Generated Questions</h3>
          <p className="text-gray-600">
            Get personalized interview questions based on your resume and target role
          </p>
        </div>

        <div className="text-center">
          <div className="bg-green-100 rounded-full p-4 w-16 h-16 mx-auto mb-4 flex items-center justify-center">
            <BarChart3 className="h-8 w-8 text-green-600" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Instant Feedback</h3>
          <p className="text-gray-600">
            Receive detailed feedback and scoring for each of your answers
          </p>
        </div>

        <div className="text-center">
          <div className="bg-purple-100 rounded-full p-4 w-16 h-16 mx-auto mb-4 flex items-center justify-center">
            <FileText className="h-8 w-8 text-purple-600" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Learning Roadmap</h3>
          <p className="text-gray-600">
            Get a personalized plan to improve your skills and interview performance
          </p>
        </div>
      </div>
    </div>
  );
};

export default Home;