import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  BarChart3, TrendingUp, Target, Clock, Award, BookOpen,
  User, Calendar, ArrowRight, RefreshCw, Plus, Star, Briefcase,
  Zap, Users, Building, DollarSign, ChevronRight
} from 'lucide-react';
import { API_URL } from '../config/api';

const Dashboard = () => {
  const navigate = useNavigate();
  const [dashboardData, setDashboardData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    console.log('[DASHBOARD DEBUG] Fetching dashboard data...');
    try {
      const token = localStorage.getItem('token');
      console.log('[DASHBOARD DEBUG] Token exists:', !!token);
      
      const response = await fetch(
        `${API_URL}/assessment/dashboard`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          }
        }
      );

      console.log('[DASHBOARD DEBUG] Response status:', response.status);

      if (response.ok) {
        const data = await response.json();
        console.log('[DASHBOARD DEBUG] Dashboard data received:', data);
        setDashboardData(data);
      } else {
        console.error('[DASHBOARD DEBUG] Failed to fetch dashboard data:', response.status);
      }
    } catch (error) {
      console.error('[DASHBOARD DEBUG] Error fetching dashboard data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="max-w-6xl mx-auto py-12 px-4">
        <div className="bg-white rounded-xl shadow-lg p-8 text-center">
          <RefreshCw className="h-16 w-16 text-indigo-600 mx-auto mb-4 animate-spin" />
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Loading Dashboard</h2>
          <p className="text-gray-600">Please wait while we fetch your data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto py-8 px-4">
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Career Dashboard</h1>
          <p className="text-gray-600">Track your career development progress</p>
        </div>
        <button
          onClick={() => navigate('/')}
          className="flex items-center px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
        >
          <Plus className="h-5 w-5 mr-2" />
          New Assessment
        </button>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Completed Assessments</p>
              <p className="text-2xl font-bold text-gray-900">
                {dashboardData?.statistics?.completed_assessments || 0}
              </p>
            </div>
            <BarChart3 className="h-8 w-8 text-indigo-600" />
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Career Recommendations</p>
              <p className="text-2xl font-bold text-gray-900">
                {dashboardData?.career_recommendations?.length || 0}
              </p>
            </div>
            <Briefcase className="h-8 w-8 text-green-600" />
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Average Score</p>
              <p className="text-2xl font-bold text-gray-900">
                {Math.round(dashboardData?.statistics?.average_overall_score || 0)}%
              </p>
            </div>
            <TrendingUp className="h-8 w-8 text-purple-600" />
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Assessments</p>
              <p className="text-2xl font-bold text-gray-900">
                {dashboardData?.statistics?.total_assessments || 0}
              </p>
            </div>
            <Target className="h-8 w-8 text-orange-600" />
          </div>
        </div>
      </div>

      {/* Recent Assessments and Career Recommendations */}
      <div className="grid lg:grid-cols-2 gap-8 mb-8">
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-bold text-gray-900">Recent Assessments</h2>
            <button className="text-indigo-600 hover:text-indigo-800 font-medium text-sm">
              View All
            </button>
          </div>

          <div className="space-y-4">
            {dashboardData?.assessment_history?.slice(0, 3).map((assessment, index) => (
              <div key={assessment.id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="font-semibold text-gray-900 capitalize">
                    {assessment.assessment_type} Assessment
                  </h3>
                  <span className="text-xs text-gray-500">
                    {new Date(assessment.created_at).toLocaleDateString()}
                  </span>
                </div>
                <div className="flex items-center space-x-4 mb-3">
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    assessment.status === 'completed' ? 'bg-green-100 text-green-800' :
                    assessment.status === 'processing' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-blue-100 text-blue-800'
                  }`}>
                    {assessment.status}
                  </span>
                  {assessment.overall_score && (
                    <span className="text-sm text-gray-600">
                      Score: {Math.round(assessment.overall_score)}%
                    </span>
                  )}
                </div>
                <button className="text-indigo-600 hover:text-indigo-800 font-medium text-sm flex items-center">
                  View Results
                  <ArrowRight className="h-4 w-4 ml-1" />
                </button>
              </div>
            )) || (
              <div className="text-center py-8">
                <BarChart3 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600">No assessments yet</p>
                <button
                  onClick={() => navigate('/')}
                  className="mt-4 text-indigo-600 hover:text-indigo-800 font-medium"
                >
                  Take your first assessment →
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Career Recommendations */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-bold text-gray-900">Career Recommendations</h2>
            <button 
              onClick={() => navigate('/roadmap')}
              className="text-indigo-600 hover:text-indigo-800 font-medium text-sm"
            >
              View All
            </button>
          </div>

          <div className="space-y-4">
            {dashboardData?.career_recommendations?.slice(0, 3).map((recommendation, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="font-semibold text-gray-900">
                    {recommendation.career_title}
                  </h3>
                  <div className="flex items-center">
                    <Star className="h-4 w-4 text-yellow-500 mr-1" />
                    <span className="text-sm font-medium text-gray-700">
                      {Math.round(recommendation.match_score)}%
                    </span>
                  </div>
                </div>
                
                <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                  {recommendation.reasoning}
                </p>
                
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
                      {recommendation.field}
                    </span>
                    {recommendation.salary_range && (
                      <span className="text-xs text-gray-500 flex items-center">
                        <DollarSign className="h-3 w-3 mr-1" />
                        {recommendation.salary_range.entry_level}
                      </span>
                    )}
                  </div>
                  <button 
                    onClick={() => navigate('/roadmap', { state: { career: recommendation } })}
                    className="text-indigo-600 hover:text-indigo-800 text-sm flex items-center"
                  >
                    Learn More
                    <ChevronRight className="h-4 w-4 ml-1" />
                  </button>
                </div>
              </div>
            )) || (
              <div className="text-center py-8">
                <Briefcase className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600">No career recommendations yet</p>
                <button
                  onClick={() => navigate('/')}
                  className="mt-4 text-indigo-600 hover:text-indigo-800 font-medium"
                >
                  Complete assessment for recommendations →
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Recommended Actions */}
      <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
        <h2 className="text-xl font-bold text-gray-900 mb-6">Recommended Actions</h2>
        
        <div className="grid md:grid-cols-3 gap-6">
          <div className="border border-gray-200 rounded-lg p-6 text-center">
            <BookOpen className="h-12 w-12 text-indigo-600 mx-auto mb-4" />
            <h3 className="font-semibold text-gray-900 mb-2">Continue Learning</h3>
            <p className="text-gray-600 text-sm mb-4">
              Follow your personalized learning roadmap
            </p>
            <button
              onClick={() => navigate('/roadmap')}
              className="text-indigo-600 hover:text-indigo-800 font-medium"
            >
              View Roadmap →
            </button>
          </div>

          <div className="border border-gray-200 rounded-lg p-6 text-center">
            <BarChart3 className="h-12 w-12 text-green-600 mx-auto mb-4" />
            <h3 className="font-semibold text-gray-900 mb-2">Retake Assessment</h3>
            <p className="text-gray-600 text-sm mb-4">
              Update your profile with new skills and interests
            </p>
            <button
              onClick={() => navigate('/')}
              className="text-green-600 hover:text-green-800 font-medium"
            >
              Start Assessment →
            </button>
          </div>

          <div className="border border-gray-200 rounded-lg p-6 text-center">
            <Award className="h-12 w-12 text-purple-600 mx-auto mb-4" />
            <h3 className="font-semibold text-gray-900 mb-2">Explore Careers</h3>
            <p className="text-gray-600 text-sm mb-4">
              Discover new career opportunities matching your profile
            </p>
            <button className="text-purple-600 hover:text-purple-800 font-medium">
              Explore Careers →
            </button>
          </div>
        </div>
      </div>

      {/* Progress Chart */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-6">Learning Progress</h2>
        
        {dashboardData?.learning_progress ? (
          <div className="space-y-6">
            {dashboardData.learning_progress.map((progress, index) => (
              <div key={index} className="border-b border-gray-200 pb-4 last:border-b-0">
                <div className="flex justify-between items-center mb-2">
                  <h3 className="font-semibold text-gray-900">{progress.skill_name}</h3>
                  <span className="text-sm text-gray-600">{progress.completion}% complete</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div
                    className="bg-gradient-to-r from-indigo-500 to-purple-600 h-3 rounded-full"
                    style={{ width: `${progress.completion}%` }}
                  ></div>
                </div>
                <p className="text-sm text-gray-600 mt-2">
                  Next milestone: {progress.next_milestone}
                </p>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <TrendingUp className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Start Your Learning Journey</h3>
            <p className="text-gray-600 mb-6">
              Complete an assessment and create a learning roadmap to track your progress
            </p>
            <button
              onClick={() => navigate('/')}
              className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
            >
              Get Started
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
