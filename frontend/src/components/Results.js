import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  TrendingUp, Target, BookOpen, ArrowRight, Download, 
  Share2, Star, MapPin, DollarSign, Clock, Users,
  Brain, BarChart3, Award, ExternalLink
} from 'lucide-react';

const Results = ({ results }) => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('careers');

  if (!results) {
    return (
      <div className="max-w-6xl mx-auto py-12 px-4">
        <div className="bg-white rounded-xl shadow-lg p-8 text-center">
          <Brain className="h-16 w-16 text-indigo-600 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Generating Your Results</h2>
          <p className="text-gray-600">Please wait while we analyze your responses...</p>
        </div>
      </div>
    );
  }

  console.log('[RESULTS DEBUG] Received results:', results);

  // Handle both old and new result formats
  const assessment_results = results.assessment_results || results.assessment || {};
  const career_recommendations = results.career_recommendations || results.recommendations || {};
  const recommendations_list = career_recommendations.recommendations || [];
  const timeSpent = results.timeSpent || 0;
  const assessmentType = results.assessmentType || 'comprehensive';

  console.log('[RESULTS DEBUG] Parsed data:', {
    assessment_results,
    career_recommendations,
    recommendations_list: recommendations_list.length,
    timeSpent,
    assessmentType
  });

  const handleDownloadReport = () => {
    // Generate and download comprehensive report
    const reportData = {
      assessment_results: assessment_results,
      career_recommendations: career_recommendations,
      generated_at: new Date().toISOString()
    };
    
    const blob = new Blob([JSON.stringify(reportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'career-assessment-report.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleCreateLearningPath = async (career, recommendation) => {
    console.log('[RESULTS DEBUG] Creating learning path for:', career.title);
    
    try {
      // First store the data locally for immediate navigation
      const learningPathData = {
        career: career,
        recommendation: recommendation,
        skills_to_develop: recommendation?.missing_skills || [],
        matching_skills: recommendation?.matching_skills || [],
        assessment_results: assessment_results
      };
      
      localStorage.setItem('learningPathData', JSON.stringify(learningPathData));
      
      // Navigate to roadmap page immediately
      navigate('/roadmap', { 
        state: { 
          careerTitle: career.title,
          careerField: career.field,
          skillsToLearn: recommendation?.missing_skills || [],
          currentSkills: recommendation?.matching_skills || []
        }
      });
      
    } catch (error) {
      console.error('[RESULTS DEBUG] Error creating learning path:', error);
      // Fallback: just navigate to roadmap page
      navigate('/roadmap');
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="max-w-6xl mx-auto py-8 px-4">
      {/* Results Header */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-xl p-8 text-white mb-8">
        <div className="text-center">
          <Award className="h-16 w-16 mx-auto mb-4" />
          <h1 className="text-3xl font-bold mb-4">Your Career Assessment Results</h1>
          <p className="text-xl opacity-90 mb-6">
            Based on your responses, we've identified your ideal career paths and development opportunities
          </p>
          <div className="flex justify-center space-x-8 text-sm">
            <div className="flex items-center">
              <Clock className="h-4 w-4 mr-1" />
              <span>Completed in {formatTime(timeSpent)}</span>
            </div>
            <div className="flex items-center">
              <Brain className="h-4 w-4 mr-1" />
              <span className="capitalize">{assessmentType} Assessment</span>
            </div>
            <div className="flex items-center">
              <Target className="h-4 w-4 mr-1" />
              <span>{recommendations_list.length} Career Matches</span>
            </div>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex justify-center space-x-4 mb-8">
        <button
          onClick={handleDownloadReport}
          className="flex items-center px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
        >
          <Download className="h-5 w-5 mr-2" />
          Download Report
        </button>
        <button
          onClick={() => {
            if (recommendations_list.length > 0) {
              handleCreateLearningPath(recommendations_list[0].career || recommendations_list[0], recommendations_list[0]);
            } else {
              navigate('/roadmap');
            }
          }}
          className="flex items-center px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
        >
          <BookOpen className="h-5 w-5 mr-2" />
          View Learning Path
        </button>
        <button className="flex items-center px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors">
          <Share2 className="h-5 w-5 mr-2" />
          Share Results
        </button>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-xl shadow-lg mb-8">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            {[
              { id: 'careers', label: 'Career Matches', icon: <Target className="h-5 w-5" /> },
              { id: 'skills', label: 'Skills Analysis', icon: <BarChart3 className="h-5 w-5" /> },
              { id: 'insights', label: 'Personality Insights', icon: <Brain className="h-5 w-5" /> }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center py-4 px-2 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-indigo-500 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab.icon}
                <span className="ml-2">{tab.label}</span>
              </button>
            ))}
          </nav>
        </div>

        <div className="p-6">
          {/* Career Matches Tab */}
          {activeTab === 'careers' && (
            <div className="space-y-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Recommended Career Paths</h2>
              
              {recommendations_list.length > 0 ? (
                recommendations_list.map((recommendation, index) => {
                  const career = recommendation.career || recommendation;
                  
                  // Format salary range
                  const formatSalary = (min, max) => {
                    if (!min && !max) return 'Varies by experience';
                    const formatNumber = (num) => {
                      if (num >= 100000) return `₹${(num / 100000).toFixed(1)}L`;
                      if (num >= 1000) return `₹${(num / 1000).toFixed(0)}K`;
                      return `₹${num}`;
                    };
                    return `${formatNumber(min || 0)} - ${formatNumber(max || min || 0)}`;
                  };
                  
                  const salaryRange = formatSalary(career.entry_level_salary, career.senior_level_salary);
                  
                  return (
                    <div key={index} className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
                      <div className="flex justify-between items-start mb-4">
                        <div className="flex-1">
                          <div className="flex items-center mb-2">
                            <h3 className="text-xl font-semibold text-gray-900">{career.title}</h3>
                            <div className="ml-3 flex items-center">
                              <Star className="h-4 w-4 text-yellow-400 fill-current" />
                              <span className="ml-1 text-sm font-medium text-gray-600">
                                {Math.round(recommendation.match_score || career.match_score || 0)}% match
                              </span>
                            </div>
                          </div>
                          <p className="text-gray-600 mb-4">{career.description}</p>
                          
                          {/* Match reasoning */}
                          {recommendation.reasoning && (
                            <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-4">
                              <h4 className="font-medium text-blue-900 mb-1">Why this matches you:</h4>
                              <p className="text-blue-800 text-sm">{recommendation.reasoning}</p>
                            </div>
                          )}
                        </div>
                      </div>

                      <div className="grid md:grid-cols-3 gap-4 mb-4">
                        <div className="flex items-center text-sm text-gray-600">
                          <DollarSign className="h-4 w-4 mr-2" />
                          <span>{salaryRange}</span>
                        </div>
                        <div className="flex items-center text-sm text-gray-600">
                          <TrendingUp className="h-4 w-4 mr-2" />
                          <span>{career.growth_rate ? `${career.growth_rate}% growth` : 'Positive outlook'}</span>
                        </div>
                        <div className="flex items-center text-sm text-gray-600">
                          <MapPin className="h-4 w-4 mr-2" />
                          <span className="capitalize">{career.field || 'Various fields'}</span>
                        </div>
                      </div>

                      {/* Skills sections */}
                      {(recommendation.matching_skills?.length > 0 || recommendation.missing_skills?.length > 0) && (
                        <div className="grid md:grid-cols-2 gap-4 mb-4">
                          {/* Matching Skills */}
                          {recommendation.matching_skills?.length > 0 && (
                            <div>
                              <h4 className="font-medium text-green-900 mb-2">Your Matching Skills:</h4>
                              <div className="flex flex-wrap gap-2">
                                {recommendation.matching_skills.slice(0, 4).map((skill, skillIndex) => (
                                  <span
                                    key={skillIndex}
                                    className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm"
                                  >
                                    {skill}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}
                          
                          {/* Missing Skills */}
                          {recommendation.missing_skills?.length > 0 && (
                            <div>
                              <h4 className="font-medium text-orange-900 mb-2">Skills to Develop:</h4>
                              <div className="flex flex-wrap gap-2">
                                {recommendation.missing_skills.slice(0, 4).map((skill, skillIndex) => (
                                  <span
                                    key={skillIndex}
                                    className="px-3 py-1 bg-orange-100 text-orange-700 rounded-full text-sm"
                                  >
                                    {skill}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      )}

                      {/* Skills gap score */}
                      {recommendation.skills_gap_score && (
                        <div className="mb-4">
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-sm font-medium text-gray-700">Skills Readiness</span>
                            <span className="text-sm text-gray-600">{recommendation.skills_gap_score}%</span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div
                              className="bg-gradient-to-r from-orange-400 to-green-500 h-2 rounded-full"
                              style={{ width: `${recommendation.skills_gap_score}%` }}
                            ></div>
                          </div>
                        </div>
                      )}

                      <div className="flex justify-between items-center">
                        <div className="text-sm text-gray-500">
                          Job Market Score: {career.job_market_score ? `${career.job_market_score}/10` : 'N/A'}
                        </div>
                        <button 
                          onClick={() => handleCreateLearningPath(career, recommendation)}
                          className="flex items-center px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors text-sm"
                        >
                          Create Learning Path
                          <ArrowRight className="h-4 w-4 ml-2" />
                        </button>
                      </div>
                    </div>
                  );
                })
              ) : (
                <div className="text-center py-8">
                  <Target className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No Career Matches Found</h3>
                  <p className="text-gray-600">Try taking the assessment again or contact support.</p>
                </div>
              )}
            </div>
          )}

          {/* Skills Analysis Tab */}
          {activeTab === 'skills' && (
            <div className="space-y-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Skills Analysis</h2>
              
              {assessment_results?.skills_analysis ? (
                <div className="space-y-6">
                  {/* Strengths */}
                  <div className="bg-green-50 border border-green-200 rounded-lg p-6">
                    <h3 className="text-lg font-semibold text-green-800 mb-4 flex items-center">
                      <Award className="h-5 w-5 mr-2" />
                      Your Strengths
                    </h3>
                    <div className="grid md:grid-cols-2 gap-4">
                      {assessment_results.skills_analysis.strengths?.map((strength, index) => (
                        <div key={index} className="flex items-center">
                          <div className="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
                          <span className="text-green-700">{strength}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Areas for Development */}
                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
                    <h3 className="text-lg font-semibold text-yellow-800 mb-4 flex items-center">
                      <TrendingUp className="h-5 w-5 mr-2" />
                      Areas for Development
                    </h3>
                    <div className="grid md:grid-cols-2 gap-4">
                      {assessment_results.skills_analysis.development_areas?.map((area, index) => (
                        <div key={index} className="flex items-center">
                          <div className="w-2 h-2 bg-yellow-500 rounded-full mr-3"></div>
                          <span className="text-yellow-700">{area}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Skill Scores */}
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Skill Breakdown</h3>
                    <div className="space-y-4">
                      {assessment_results.skills_analysis.skill_scores?.map((skill, index) => (
                        <div key={index} className="flex items-center justify-between">
                          <span className="font-medium text-gray-900">{skill.name}</span>
                          <div className="flex items-center space-x-3">
                            <div className="w-32 bg-gray-200 rounded-full h-2">
                              <div
                                className="bg-indigo-600 h-2 rounded-full"
                                style={{ width: `${skill.score}%` }}
                              ></div>
                            </div>
                            <span className="text-sm text-gray-600 w-12">{skill.score}%</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8">
                  <BarChart3 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">Skills Analysis Coming Soon</h3>
                  <p className="text-gray-600">Detailed skills analysis will be available after assessment completion.</p>
                </div>
              )}
            </div>
          )}

          {/* Personality Insights Tab */}
          {activeTab === 'insights' && (
            <div className="space-y-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Personality Insights</h2>
              
              {assessment_results?.personality_insights ? (
                <div className="space-y-6">
                  <div className="bg-purple-50 border border-purple-200 rounded-lg p-6">
                    <h3 className="text-lg font-semibold text-purple-800 mb-4 flex items-center">
                      <Brain className="h-5 w-5 mr-2" />
                      Your Work Style
                    </h3>
                    <p className="text-purple-700">{assessment_results.personality_insights.work_style}</p>
                  </div>

                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                    <h3 className="text-lg font-semibold text-blue-800 mb-4 flex items-center">
                      <Users className="h-5 w-5 mr-2" />
                      Team Collaboration
                    </h3>
                    <p className="text-blue-700">{assessment_results.personality_insights.collaboration_style}</p>
                  </div>

                  <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-6">
                    <h3 className="text-lg font-semibold text-indigo-800 mb-4 flex items-center">
                      <Target className="h-5 w-5 mr-2" />
                      Motivation Factors
                    </h3>
                    <div className="grid md:grid-cols-2 gap-4">
                      {assessment_results.personality_insights.motivation_factors?.map((factor, index) => (
                        <div key={index} className="flex items-center">
                          <div className="w-2 h-2 bg-indigo-500 rounded-full mr-3"></div>
                          <span className="text-indigo-700">{factor}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8">
                  <Brain className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">Personality Insights Coming Soon</h3>
                  <p className="text-gray-600">Detailed personality analysis will be available after assessment completion.</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Next Steps */}
      <div className="bg-white rounded-xl shadow-lg p-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">Your Next Steps</h2>
        <div className="grid md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="bg-indigo-100 p-4 rounded-full w-16 h-16 mx-auto mb-4 flex items-center justify-center">
              <BookOpen className="h-8 w-8 text-indigo-600" />
            </div>
            <h3 className="font-semibold text-gray-900 mb-2">Start Learning</h3>
            <p className="text-gray-600 text-sm mb-4">
              Follow personalized learning roadmaps for your chosen career path
            </p>
            <button
              onClick={() => navigate('/roadmap')}
              className="text-indigo-600 font-medium hover:text-indigo-800"
            >
              View Roadmap →
            </button>
          </div>

          <div className="text-center">
            <div className="bg-green-100 p-4 rounded-full w-16 h-16 mx-auto mb-4 flex items-center justify-center">
              <Target className="h-8 w-8 text-green-600" />
            </div>
            <h3 className="font-semibold text-gray-900 mb-2">Set Goals</h3>
            <p className="text-gray-600 text-sm mb-4">
              Create specific, measurable goals for your career development
            </p>
            <button className="text-green-600 font-medium hover:text-green-800">
              Set Goals →
            </button>
          </div>

          <div className="text-center">
            <div className="bg-purple-100 p-4 rounded-full w-16 h-16 mx-auto mb-4 flex items-center justify-center">
              <Users className="h-8 w-8 text-purple-600" />
            </div>
            <h3 className="font-semibold text-gray-900 mb-2">Connect</h3>
            <p className="text-gray-600 text-sm mb-4">
              Network with professionals in your field and find mentors
            </p>
            <button className="text-purple-600 font-medium hover:text-purple-800">
              Find Mentors →
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Results;
