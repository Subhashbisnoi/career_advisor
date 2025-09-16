import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDropzone } from 'react-dropzone';
import { 
  Upload, FileText, Brain, Target, BarChart3, ArrowRight, 
  Compass, BookOpen, TrendingUp, Users, Award, Star,
  CheckCircle, Clock, MapPin, DollarSign
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import AuthModal from './auth/AuthModal';
import { API_URL } from '../config/api';

const Home = ({ onStartAssessment }) => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [documentFile, setDocumentFile] = useState(null);
  const [formData, setFormData] = useState({
    educationLevel: '',
    fieldOfStudy: '',
    careerGoals: '',
    interests: [],
    experienceLevel: '',
    preferredLocation: '',
    salaryExpectations: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [assessmentType, setAssessmentType] = useState('comprehensive');

  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0];
      if (file.type === 'application/pdf') {
        setDocumentFile(file);
        setError('');
      } else {
        setError('Please upload a PDF file (resume or transcript)');
      }
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf']
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
  };

  const handleInterestToggle = (interest) => {
    setFormData(prev => ({
      ...prev,
      interests: prev.interests.includes(interest)
        ? prev.interests.filter(i => i !== interest)
        : [...prev.interests, interest]
    }));
  };

  const handleStartAssessment = async (e) => {
    e.preventDefault();
    
    if (!formData.educationLevel) {
      setError('Please select your education level');
      return;
    }

    if (formData.interests.length === 0) {
      setError('Please select at least one area of interest');
      return;
    }

    const assessmentData = {
      assessmentType,
      userBackground: {
        education_level: formData.educationLevel,
        field_of_study: formData.fieldOfStudy,
        career_goals: formData.careerGoals,
        interests: formData.interests,
        experience_level: formData.experienceLevel,
        preferred_location: formData.preferredLocation,
        salary_expectations: formData.salaryExpectations
      },
      documentFile
    };

    if (!user) {
      // Store assessment data for after login
      sessionStorage.setItem('pendingAssessment', JSON.stringify(assessmentData));
      setShowAuthModal(true);
      return;
    }

    await startAssessment(assessmentData);
  };

  const startAssessment = async (data) => {
    setIsLoading(true);
    setError('');
    
    try {
      // Get auth token
      const token = localStorage.getItem('token');
      const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      };

      // Start career assessment
      const response = await fetch(
        `${API_URL}/assessment/start`,
        {
          method: 'POST',
          headers,
          body: JSON.stringify({
            assessment_type: data.assessmentType,
            user_background: data.userBackground
          })
        }
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to start assessment');
      }

      const result = await response.json();

      // Pass data to parent component
      if (onStartAssessment) {
        onStartAssessment({
          assessmentId: result.assessment_id,
          threadId: result.thread_id,
          assessmentType: result.assessment_type,
          questions: result.questions,
          userBackground: data.userBackground
        });
      }

      // Navigate to assessment page
      navigate('/assessment');
    } catch (err) {
      setError(err.message || 'Failed to start assessment. Please try again.');
      console.error('Assessment error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAuthSuccess = () => {
    setShowAuthModal(false);
    
    // Check if there's a pending assessment
    const pendingAssessment = sessionStorage.getItem('pendingAssessment');
    if (pendingAssessment) {
      const assessmentData = JSON.parse(pendingAssessment);
      sessionStorage.removeItem('pendingAssessment');
      startAssessment(assessmentData);
    }
  };

  // Close modal when user becomes authenticated
  React.useEffect(() => {
    if (user && showAuthModal) {
      handleAuthSuccess();
    }
  }, [user, showAuthModal]);

  const interestOptions = [
    'Technology & Programming',
    'Healthcare & Medicine',
    'Business & Finance',
    'Education & Training',
    'Design & Creative Arts',
    'Engineering & Manufacturing',
    'Research & Development',
    'Social Impact & NGO',
    'Government & Public Service',
    'Entrepreneurship',
    'Marketing & Communications',
    'Data Science & Analytics'
  ];

  const assessmentTypes = [
    {
      value: 'skills',
      title: 'Skills Assessment',
      description: 'Focus on your technical and soft skills analysis',
      icon: <BarChart3 className="h-6 w-6" />,
      duration: '15-20 minutes',
      features: ['Technical Skills', 'Soft Skills', 'Skill Gaps', 'Improvement Areas']
    },
    {
      value: 'comprehensive',
      title: 'Comprehensive Assessment',
      description: 'Complete evaluation covering skills, interests, and personality',
      icon: <Brain className="h-6 w-6" />,
      duration: '25-30 minutes',
      features: ['Full Skills Analysis', 'Career Matching', 'Personality Insights', 'Learning Roadmap']
    },
    {
      value: 'interest',
      title: 'Interest & Aptitude',
      description: 'Discover careers based on your interests and natural aptitudes',
      icon: <Compass className="h-6 w-6" />,
      duration: '10-15 minutes',
      features: ['Interest Mapping', 'Aptitude Tests', 'Career Fit', 'Work Environment']
    }
  ];

  return (
    <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
      {/* Hero Section */}
      <div className="text-center mb-16">
        <h1 className="text-5xl font-bold text-gray-900 mb-6">
          Discover Your <span className="text-indigo-600">Perfect Career Path</span>
        </h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-8">
          Get personalized career recommendations based on your skills, interests, and the evolving Indian job market. 
          Our AI-powered platform helps you make informed decisions about your future.
        </p>
        
        {/* Key Benefits */}
        <div className="flex flex-wrap justify-center gap-4 mb-8">
          <div className="flex items-center bg-indigo-50 px-4 py-2 rounded-full">
            <Brain className="h-5 w-5 text-indigo-600 mr-2" />
            <span className="text-indigo-700 font-medium">AI-Powered Analysis</span>
          </div>
          <div className="flex items-center bg-green-50 px-4 py-2 rounded-full">
            <Target className="h-5 w-5 text-green-600 mr-2" />
            <span className="text-green-700 font-medium">Personalized Recommendations</span>
          </div>
          <div className="flex items-center bg-purple-50 px-4 py-2 rounded-full">
            <TrendingUp className="h-5 w-5 text-purple-600 mr-2" />
            <span className="text-purple-700 font-medium">Market Insights</span>
          </div>
          <div className="flex items-center bg-orange-50 px-4 py-2 rounded-full">
            <BookOpen className="h-5 w-5 text-orange-600 mr-2" />
            <span className="text-orange-700 font-medium">Learning Roadmaps</span>
          </div>
        </div>

        {/* Success Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 max-w-2xl mx-auto mb-12">
          <div className="text-center">
            <div className="text-2xl font-bold text-indigo-600">10,000+</div>
            <div className="text-sm text-gray-600">Students Guided</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">95%</div>
            <div className="text-sm text-gray-600">Accuracy Rate</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">200+</div>
            <div className="text-sm text-gray-600">Career Paths</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-orange-600">24/7</div>
            <div className="text-sm text-gray-600">AI Support</div>
          </div>
        </div>
      </div>

      {/* Assessment Form */}
      <div className="bg-white shadow-xl rounded-2xl p-8 mb-12">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">Start Your Career Assessment</h2>
          <p className="text-gray-600 max-w-2xl mx-auto">
            Complete a comprehensive assessment to get personalized career recommendations tailored to the Indian job market
          </p>
        </div>

        <form onSubmit={handleStartAssessment} className="space-y-8">
          {/* Assessment Type Selection */}
          <div>
            <label className="block text-lg font-medium text-gray-700 mb-6 text-center">
              Choose Your Assessment Type
            </label>
            <div className="grid md:grid-cols-3 gap-6">
              {assessmentTypes.map((type) => (
                <div
                  key={type.value}
                  className={`border-2 rounded-xl p-6 cursor-pointer transition-all ${
                    assessmentType === type.value
                      ? 'border-indigo-500 bg-indigo-50 shadow-lg'
                      : 'border-gray-200 hover:border-indigo-300 hover:shadow-md'
                  }`}
                  onClick={() => setAssessmentType(type.value)}
                >
                  <div className="text-center">
                    <div className={`p-3 rounded-full w-16 h-16 mx-auto mb-4 flex items-center justify-center ${
                      assessmentType === type.value ? 'bg-indigo-100 text-indigo-600' : 'bg-gray-100 text-gray-600'
                    }`}>
                      {type.icon}
                    </div>
                    <h3 className="text-lg font-semibold mb-2">{type.title}</h3>
                    <p className="text-sm text-gray-600 mb-3">{type.description}</p>
                    <div className="text-xs text-gray-500 mb-3">⏱️ {type.duration}</div>
                    <div className="space-y-1">
                      {type.features.map((feature, index) => (
                        <div key={index} className="flex items-center text-xs text-gray-600">
                          <CheckCircle className="h-3 w-3 text-green-500 mr-2" />
                          <span>{feature}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Personal Information */}
          <div className="grid md:grid-cols-2 gap-6">
            {/* Education Level */}
            <div>
              <label htmlFor="educationLevel" className="block text-sm font-medium text-gray-700 mb-2">
                Education Level *
              </label>
              <select
                name="educationLevel"
                id="educationLevel"
                value={formData.educationLevel}
                onChange={handleInputChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
                required
              >
                <option value="">Select your education level</option>
                <option value="high_school">High School (10+2)</option>
                <option value="bachelor">Bachelor's Degree</option>
                <option value="master">Master's Degree</option>
                <option value="phd">PhD</option>
                <option value="diploma">Diploma</option>
                <option value="certification">Professional Certification</option>
              </select>
            </div>

            {/* Experience Level */}
            <div>
              <label htmlFor="experienceLevel" className="block text-sm font-medium text-gray-700 mb-2">
                Experience Level
              </label>
              <select
                name="experienceLevel"
                id="experienceLevel"
                value={formData.experienceLevel}
                onChange={handleInputChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
              >
                <option value="">Select your experience level</option>
                <option value="student">Student/Recent Graduate</option>
                <option value="0-1">0-1 years</option>
                <option value="1-3">1-3 years</option>
                <option value="3-5">3-5 years</option>
                <option value="5+">5+ years</option>
              </select>
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            {/* Field of Study */}
            <div>
              <label htmlFor="fieldOfStudy" className="block text-sm font-medium text-gray-700 mb-2">
                Field of Study
              </label>
              <input
                type="text"
                name="fieldOfStudy"
                id="fieldOfStudy"
                value={formData.fieldOfStudy}
                onChange={handleInputChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
                placeholder="e.g., Computer Science, Business Administration"
              />
            </div>

            {/* Preferred Location */}
            <div>
              <label htmlFor="preferredLocation" className="block text-sm font-medium text-gray-700 mb-2">
                Preferred Work Location
              </label>
              <select
                name="preferredLocation"
                id="preferredLocation"
                value={formData.preferredLocation}
                onChange={handleInputChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
              >
                <option value="">Select preferred location</option>
                <option value="metro">Metro Cities (Mumbai, Delhi, Bangalore)</option>
                <option value="tier1">Tier 1 Cities (Pune, Chennai, Hyderabad)</option>
                <option value="tier2">Tier 2 Cities</option>
                <option value="remote">Remote Work</option>
                <option value="flexible">Flexible/Any Location</option>
              </select>
            </div>
          </div>

          {/* Career Goals */}
          <div>
            <label htmlFor="careerGoals" className="block text-sm font-medium text-gray-700 mb-2">
              Career Goals & Aspirations
            </label>
            <textarea
              name="careerGoals"
              id="careerGoals"
              rows="4"
              value={formData.careerGoals}
              onChange={handleInputChange}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
              placeholder="Describe your career aspirations, goals, and what you want to achieve in your professional life..."
            />
          </div>

          {/* Interest Areas */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Areas of Interest * (Select all that apply)
            </label>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
              {interestOptions.map((interest) => (
                <div
                  key={interest}
                  className={`border rounded-lg p-3 cursor-pointer transition-all text-sm ${
                    formData.interests.includes(interest)
                      ? 'border-indigo-500 bg-indigo-50 text-indigo-700'
                      : 'border-gray-200 hover:border-indigo-300 hover:bg-gray-50'
                  }`}
                  onClick={() => handleInterestToggle(interest)}
                >
                  <div className="flex items-center">
                    <div className={`w-4 h-4 rounded border-2 mr-2 ${
                      formData.interests.includes(interest)
                        ? 'border-indigo-500 bg-indigo-500'
                        : 'border-gray-300'
                    }`}>
                      {formData.interests.includes(interest) && (
                        <CheckCircle className="w-3 h-3 text-white" />
                      )}
                    </div>
                    <span>{interest}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Salary Expectations */}
          <div>
            <label htmlFor="salaryExpectations" className="block text-sm font-medium text-gray-700 mb-2">
              Salary Expectations (Annual, in INR)
            </label>
            <select
              name="salaryExpectations"
              id="salaryExpectations"
              value={formData.salaryExpectations}
              onChange={handleInputChange}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
            >
              <option value="">Select salary range</option>
              <option value="0-3">₹0 - ₹3 Lakhs</option>
              <option value="3-6">₹3 - ₹6 Lakhs</option>
              <option value="6-10">₹6 - ₹10 Lakhs</option>
              <option value="10-15">₹10 - ₹15 Lakhs</option>
              <option value="15-25">₹15 - ₹25 Lakhs</option>
              <option value="25+">₹25+ Lakhs</option>
            </select>
          </div>

          {/* Document Upload */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Upload Resume or Academic Transcript (Optional)
            </label>
            <div
              {...getRootProps()}
              className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors ${
                isDragActive ? 'border-indigo-500 bg-indigo-50' : 'border-gray-300 hover:border-indigo-400'
              }`}
            >
              <input {...getInputProps()} />
              {documentFile ? (
                <div className="space-y-2">
                  <FileText className="mx-auto h-12 w-12 text-green-500" />
                  <p className="text-sm text-green-600 font-medium">
                    {documentFile.name}
                  </p>
                  <p className="text-xs text-green-500">
                    Click or drag to replace
                  </p>
                </div>
              ) : (
                <div className="space-y-2">
                  <Upload className="h-10 w-10 mx-auto text-gray-400" />
                  <p className="text-sm text-gray-600">
                    {isDragActive ? 'Drop your document here' : 'Drag and drop your resume or transcript here, or click to select'}
                  </p>
                  <p className="text-xs text-gray-500">PDF files only (max 5MB)</p>
                </div>
              )}
            </div>
            {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
          </div>

          <div className="pt-6">
            <button
              type="submit"
              disabled={isLoading}
              className="w-full flex justify-center items-center px-8 py-4 border border-transparent rounded-lg shadow-sm text-lg font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isLoading ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                  Starting your assessment...
                </>
              ) : (
                <>
                  Start Career Assessment
                  <ArrowRight className="ml-2 h-5 w-5" />
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* Features Section */}
      <div className="grid md:grid-cols-3 gap-8 mb-16">
        <div className="bg-white p-8 rounded-xl shadow-lg hover:shadow-xl transition-shadow">
          <div className="bg-indigo-100 p-4 rounded-full w-16 h-16 flex items-center justify-center mb-6">
            <Brain className="h-8 w-8 text-indigo-600" />
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-3">AI-Powered Assessment</h3>
          <p className="text-gray-600">
            Advanced AI analyzes your skills, interests, and aptitude to provide personalized career recommendations
          </p>
        </div>

        <div className="bg-white p-8 rounded-xl shadow-lg hover:shadow-xl transition-shadow">
          <div className="bg-green-100 p-4 rounded-full w-16 h-16 flex items-center justify-center mb-6">
            <Target className="h-8 w-8 text-green-600" />
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-3">Personalized Guidance</h3>
          <p className="text-gray-600">
            Get customized career paths based on your unique profile and the Indian job market dynamics
          </p>
        </div>

        <div className="bg-white p-8 rounded-xl shadow-lg hover:shadow-xl transition-shadow">
          <div className="bg-purple-100 p-4 rounded-full w-16 h-16 flex items-center justify-center mb-6">
            <BookOpen className="h-8 w-8 text-purple-600" />
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-3">Learning Roadmaps</h3>
          <p className="text-gray-600">
            Receive step-by-step learning plans with resources, timelines, and milestones for your chosen career
          </p>
        </div>

        <div className="bg-white p-8 rounded-xl shadow-lg hover:shadow-xl transition-shadow">
          <div className="bg-blue-100 p-4 rounded-full w-16 h-16 flex items-center justify-center mb-6">
            <TrendingUp className="h-8 w-8 text-blue-600" />
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-3">Market Insights</h3>
          <p className="text-gray-600">
            Stay updated with job market trends, salary insights, and emerging opportunities in India
          </p>
        </div>

        <div className="bg-white p-8 rounded-xl shadow-lg hover:shadow-xl transition-shadow">
          <div className="bg-orange-100 p-4 rounded-full w-16 h-16 flex items-center justify-center mb-6">
            <Users className="h-8 w-8 text-orange-600" />
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-3">Skills Analysis</h3>
          <p className="text-gray-600">
            Comprehensive evaluation of technical and soft skills with gap analysis for your target career
          </p>
        </div>

        <div className="bg-white p-8 rounded-xl shadow-lg hover:shadow-xl transition-shadow">
          <div className="bg-red-100 p-4 rounded-full w-16 h-16 flex items-center justify-center mb-6">
            <Award className="h-8 w-8 text-red-600" />
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-3">Progress Tracking</h3>
          <p className="text-gray-600">
            Monitor your learning journey with milestone tracking and achievement recognition
          </p>
        </div>
      </div>

      {/* Call to Action */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-2xl p-8 text-center text-white">
        <h2 className="text-3xl font-bold mb-4">Ready to Discover Your Future?</h2>
        <p className="text-xl mb-6 opacity-90">
          Join thousands of students who have found their ideal career path with our AI-powered guidance
        </p>
        <div className="flex flex-wrap justify-center gap-6 text-sm mb-6">
          <div className="flex items-center">
            <CheckCircle className="w-5 h-5 mr-2" />
            <span>Completely Free</span>
          </div>
          <div className="flex items-center">
            <CheckCircle className="w-5 h-5 mr-2" />
            <span>No Hidden Costs</span>
          </div>
          <div className="flex items-center">
            <CheckCircle className="w-5 h-5 mr-2" />
            <span>Instant Results</span>
          </div>
          <div className="flex items-center">
            <CheckCircle className="w-5 h-5 mr-2" />
            <span>Expert Guidance</span>
          </div>
        </div>
        
        {/* Testimonial */}
        <div className="bg-white bg-opacity-20 rounded-lg p-6 max-w-2xl mx-auto">
          <div className="flex items-center justify-center mb-4">
            {[...Array(5)].map((_, i) => (
              <Star key={i} className="h-5 w-5 text-yellow-300 fill-current" />
            ))}
          </div>
          <p className="text-lg mb-4 italic">
            "This platform completely changed my career direction. I discovered opportunities I never knew existed!"
          </p>
          <p className="text-sm opacity-90">- Priya S., Software Engineer</p>
        </div>
      </div>

      <AuthModal
        isOpen={showAuthModal}
        onClose={() => {
          setShowAuthModal(false);
        }}
        onSuccess={handleAuthSuccess}
        initialMode="login"
      />
    </div>
  );
};

export default Home;