import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDropzone } from 'react-dropzone';
import { useAuth } from '../contexts/AuthContext';
import AuthRequiredModal from './auth/AuthRequiredModal';

const Home = ({ onStartInterview }) => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [resumeFile, setResumeFile] = useState(null);
  const [formData, setFormData] = useState({
    role: '',
    company: '',
    experienceLevel: '',
    techStack: '',
    interviewType: ''
  });
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [errors, setErrors] = useState({});

  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles && acceptedFiles.length > 0) {
      setResumeFile(acceptedFiles[0]);
      setErrors(prev => ({ ...prev, resume: '' }));
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
    },
    multiple: false,
    maxSize: 5 * 1024 * 1024 // 5MB
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.role.trim()) {
      newErrors.role = 'Job role is required';
    }
    
    if (!formData.company.trim()) {
      newErrors.company = 'Company name is required';
    }
    
    if (!formData.experienceLevel) {
      newErrors.experienceLevel = 'Experience level is required';
    }
    
    if (!formData.interviewType) {
      newErrors.interviewType = 'Interview type is required';
    }
    
    if (!resumeFile) {
      newErrors.resume = 'Resume upload is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleStartInterview = async () => {
    if (!user) {
      setShowAuthModal(true);
      return;
    }

    if (!validateForm()) {
      return;
    }

    const interviewData = {
      ...formData,
      resumeFile
    };
    
    onStartInterview(interviewData);
    navigate('/interview');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <div className="container mx-auto px-4 py-8">
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
            AI-Powered Mock Interviews
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Practice with our advanced AI interviewer. Get real-time feedback, 
            personalized questions, and detailed performance analytics.
          </p>
        </div>

        <div className="max-w-4xl mx-auto">
          <div className="grid md:grid-cols-2 gap-8 mb-12">
            {/* Features */}
            <div className="space-y-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Why Choose AI Interviewer?</h2>
              
              <div className="flex items-start space-x-4">
                <div className="bg-blue-100 p-2 rounded-lg">
                  <span className="text-2xl">🤖</span>
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">AI-Powered Questions</h3>
                  <p className="text-gray-600">Dynamic questions tailored to your role and experience</p>
                </div>
              </div>

              <div className="flex items-start space-x-4">
                <div className="bg-green-100 p-2 rounded-lg">
                  <span className="text-2xl">📊</span>
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">Real-time Feedback</h3>
                  <p className="text-gray-600">Instant analysis and scoring of your responses</p>
                </div>
              </div>

              <div className="flex items-start space-x-4">
                <div className="bg-purple-100 p-2 rounded-lg">
                  <span className="text-2xl">📈</span>
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">Performance Analytics</h3>
                  <p className="text-gray-600">Detailed insights and improvement recommendations</p>
                </div>
              </div>

              <div className="flex items-start space-x-4">
                <div className="bg-orange-100 p-2 rounded-lg">
                  <span className="text-2xl">🎯</span>
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">Role-Specific Practice</h3>
                  <p className="text-gray-600">Customized scenarios for your target position</p>
                </div>
              </div>
            </div>

            {/* Interview Setup Form */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Start Your Mock Interview</h2>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Job Role *
                  </label>
                  <input
                    type="text"
                    name="role"
                    value={formData.role}
                    onChange={handleInputChange}
                    placeholder="e.g., Software Engineer, Product Manager"
                    className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                      errors.role ? 'border-red-500' : 'border-gray-300'
                    }`}
                  />
                  {errors.role && <p className="text-red-500 text-sm mt-1">{errors.role}</p>}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Company *
                  </label>
                  <input
                    type="text"
                    name="company"
                    value={formData.company}
                    onChange={handleInputChange}
                    placeholder="e.g., Google, Microsoft, Startup"
                    className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                      errors.company ? 'border-red-500' : 'border-gray-300'
                    }`}
                  />
                  {errors.company && <p className="text-red-500 text-sm mt-1">{errors.company}</p>}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Experience Level *
                  </label>
                  <select
                    name="experienceLevel"
                    value={formData.experienceLevel}
                    onChange={handleInputChange}
                    className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                      errors.experienceLevel ? 'border-red-500' : 'border-gray-300'
                    }`}
                  >
                    <option value="">Select experience level</option>
                    <option value="entry">Entry Level (0-2 years)</option>
                    <option value="mid">Mid Level (3-5 years)</option>
                    <option value="senior">Senior Level (6-10 years)</option>
                    <option value="lead">Lead/Principal (10+ years)</option>
                  </select>
                  {errors.experienceLevel && <p className="text-red-500 text-sm mt-1">{errors.experienceLevel}</p>}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Tech Stack / Skills
                  </label>
                  <input
                    type="text"
                    name="techStack"
                    value={formData.techStack}
                    onChange={handleInputChange}
                    placeholder="e.g., React, Python, Machine Learning"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Interview Type *
                  </label>
                  <select
                    name="interviewType"
                    value={formData.interviewType}
                    onChange={handleInputChange}
                    className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                      errors.interviewType ? 'border-red-500' : 'border-gray-300'
                    }`}
                  >
                    <option value="">Select interview type</option>
                    <option value="technical">Technical Interview</option>
                    <option value="behavioral">Behavioral Interview</option>
                    <option value="mixed">Mixed (Technical + Behavioral)</option>
                    <option value="system-design">System Design</option>
                  </select>
                  {errors.interviewType && <p className="text-red-500 text-sm mt-1">{errors.interviewType}</p>}
                </div>

                {/* Resume Upload */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Upload Resume *
                  </label>
                  <div
                    {...getRootProps()}
                    className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors ${
                      isDragActive
                        ? 'border-blue-500 bg-blue-50'
                        : errors.resume
                        ? 'border-red-500 bg-red-50'
                        : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'
                    }`}
                  >
                    <input {...getInputProps()} />
                    <div className="text-4xl mb-2">📄</div>
                    {resumeFile ? (
                      <div>
                        <p className="font-medium text-green-600">{resumeFile.name}</p>
                        <p className="text-sm text-gray-500">
                          {Math.round(resumeFile.size / 1024)} KB
                        </p>
                      </div>
                    ) : (
                      <div>
                        <p className="text-gray-600">
                          {isDragActive
                            ? 'Drop your resume here...'
                            : 'Drag & drop your resume, or click to select'
                          }
                        </p>
                        <p className="text-sm text-gray-500 mt-1">
                          PDF, DOC, DOCX (max 5MB)
                        </p>
                      </div>
                    )}
                  </div>
                  {errors.resume && <p className="text-red-500 text-sm mt-1">{errors.resume}</p>}
                </div>

                <button
                  onClick={handleStartInterview}
                  className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-blue-700 transition-colors flex items-center justify-center space-x-2"
                >
                  <span>Start Mock Interview</span>
                  <span>➡️</span>
                </button>
              </div>
            </div>
          </div>

          {/* Statistics */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
            <div className="bg-white rounded-lg p-6 shadow-sm">
              <div className="text-3xl font-bold text-blue-600">10,000+</div>
              <div className="text-gray-600">Interviews Conducted</div>
            </div>
            <div className="bg-white rounded-lg p-6 shadow-sm">
              <div className="text-3xl font-bold text-green-600">95%</div>
              <div className="text-gray-600">User Satisfaction</div>
            </div>
            <div className="bg-white rounded-lg p-6 shadow-sm">
              <div className="text-3xl font-bold text-purple-600">4.8/5</div>
              <div className="text-gray-600">Average Rating</div>
            </div>
          </div>
        </div>
      </div>

      {showAuthModal && (
        <AuthRequiredModal 
          isOpen={showAuthModal}
          onClose={() => setShowAuthModal(false)}
          message="Please sign up or log in to start your mock interview"
        />
      )}
    </div>
  );
};

export default Home;
