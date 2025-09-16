import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { 
  MapPin, Clock, BookOpen, CheckCircle, ArrowRight, 
  Target, TrendingUp, Award, ExternalLink, Play,
  Calendar, Users, Star, Download, Check, X
} from 'lucide-react';

const CareerRoadmap = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [roadmapData, setRoadmapData] = useState(null);
  const [selectedCareer, setSelectedCareer] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [activePhase, setActivePhase] = useState(0);
  const [learningPathData, setLearningPathData] = useState(null);

  useEffect(() => {
    // Check for learning path data from Results component
    const storedLearningPath = localStorage.getItem('learningPathData');
    const locationState = location.state;
    
    if (storedLearningPath) {
      const parsedData = JSON.parse(storedLearningPath);
      setLearningPathData(parsedData);
      console.log('[ROADMAP DEBUG] Found learning path data:', parsedData);
      
      // Generate roadmap for the specific career
      generateRoadmapFromCareerData(parsedData);
    } else if (locationState && locationState.careerTitle) {
      console.log('[ROADMAP DEBUG] Found location state:', locationState);
      generateRoadmapFromLocationState(locationState);
    } else {
      // Fallback to fetching existing roadmaps
      fetchRoadmapData();
    }
  }, [location]);

  const generateRoadmapFromCareerData = async (pathData) => {
    try {
      const career = pathData.career;
      const recommendation = pathData.recommendation;
      const skillsToLearn = pathData.skills_to_develop || [];
      
      console.log('[ROADMAP DEBUG] Generating roadmap for:', career.title);
      console.log('[ROADMAP DEBUG] Skills to learn:', skillsToLearn);
      
      // Call the backend API to generate the roadmap
      const token = localStorage.getItem('token');
      const response = await fetch(
        `${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/roadmap/generate-from-recommendation`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            career: career,
            recommendation: recommendation,
            skills_to_develop: skillsToLearn,
            matching_skills: pathData.matching_skills || []
          })
        }
      );

      if (response.ok) {
        const roadmap = await response.json();
        console.log('[ROADMAP DEBUG] Generated roadmap:', roadmap);
        setSelectedCareer(roadmap);
        setRoadmapData({ roadmaps: [roadmap] });
      } else {
        console.error('Failed to generate roadmap:', await response.text());
        // Fallback to custom roadmap
        const customRoadmap = createCustomRoadmap(career, pathData);
        setSelectedCareer(customRoadmap);
        setRoadmapData({ roadmaps: [customRoadmap] });
      }
      setIsLoading(false);
      
    } catch (error) {
      console.error('Failed to generate roadmap from career data:', error);
      // Fallback to custom roadmap
      const customRoadmap = createCustomRoadmap(pathData.career, pathData);
      setSelectedCareer(customRoadmap);
      setRoadmapData({ roadmaps: [customRoadmap] });
      setIsLoading(false);
    }
  };

  const generateRoadmapFromLocationState = async (state) => {
    try {
      const customRoadmap = createCustomRoadmapFromState(state);
      setSelectedCareer(customRoadmap);
      setRoadmapData({ roadmaps: [customRoadmap] });
      setIsLoading(false);
    } catch (error) {
      console.error('Failed to generate roadmap from location state:', error);
      setIsLoading(false);
    }
  };

  const fetchRoadmapData = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(
        `${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/roadmap/`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          }
        }
      );

      if (response.ok) {
        const data = await response.json();
        console.log('[ROADMAP DEBUG] Fetched roadmaps:', data);
        setRoadmapData(data);
        if (data.roadmaps && data.roadmaps.length > 0) {
          setSelectedCareer(data.roadmaps[0]);
        }
      }
    } catch (error) {
      console.error('Failed to fetch roadmap data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const updateStepProgress = async (roadmapId, phaseId, stepId, isCompleted) => {
    try {
      const token = localStorage.getItem('token');
      
      if (isCompleted) {
        // Mark as completed
        const response = await fetch(
          `${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/roadmap/update-progress`,
          {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              roadmap_id: roadmapId,
              phase_id: phaseId,
              step_id: stepId,
              notes: "Completed via roadmap interface"
            })
          }
        );

        if (response.ok) {
          const result = await response.json();
          console.log('[ROADMAP DEBUG] Updated progress:', result);
          
          // Update the local state
          setSelectedCareer(prev => {
            const updated = { ...prev };
            updated.phases = updated.phases.map(phase => {
              if (phase.phase_id === phaseId) {
                const updatedPhase = { ...phase };
                updatedPhase.steps = updatedPhase.steps.map(step => {
                  if (step.step_id === stepId) {
                    return { ...step, is_completed: true, completed_at: new Date().toISOString() };
                  }
                  return step;
                });
                return updatedPhase;
              }
              return phase;
            });
            
            // Update progress
            updated.progress = {
              ...updated.progress,
              completed_steps: result.completed_steps,
              overall_progress: result.progress_percentage
            };
            
            return updated;
          });
        }
      }
    } catch (error) {
      console.error('Failed to update step progress:', error);
    }
  };

  const createCustomRoadmap = (career, pathData) => {
    // This is kept as fallback for the old format
    const skillsToLearn = pathData.skills_to_develop || [];
    const currentSkills = pathData.matching_skills || [];
    
    const phases = [];
    
    // Foundation Phase
    if (skillsToLearn.length > 0) {
      phases.push({
        phase_id: "foundation",
        title: "Foundation Phase",
        description: "Build essential skills for your career path",
        estimated_duration_weeks: 6,
        steps: skillsToLearn.slice(0, 3).map((skill, index) => ({
          step_id: `foundation_${index + 1}`,
          title: `Learn ${skill} Fundamentals`,
          description: `Master the basics of ${skill} through structured learning`,
          estimated_hours: 40,
          difficulty_level: "beginner",
          step_type: "learning",
          is_completed: false,
          resources: [{
            type: "course",
            title: `${skill} Fundamentals Course`,
            provider: "Online Platform",
            url: "#",
            cost: "Free"
          }]
        })),
        skills_focus: skillsToLearn.slice(0, 3)
      });
    }
    
    return {
      id: Date.now(),
      career_path: career.title,
      description: career.description || `Comprehensive learning path for ${career.title}`,
      timeline_months: 6,
      phases: phases,
      total_steps: phases.reduce((total, phase) => total + phase.steps.length, 0),
      completed_steps: 0,
      progress: {
        completed_steps: 0,
        total_steps: phases.reduce((total, phase) => total + phase.steps.length, 0),
        overall_progress: 0
      }
    };
  };

  const createCustomRoadmapFromState = (state) => {
    return createCustomRoadmap({
      title: state.careerTitle,
      description: `Learning path for ${state.careerTitle} in ${state.careerField}`,
      field: state.careerField
    }, {
      skills_to_develop: state.skillsToLearn || [],
      matching_skills: state.currentSkills || []
    });
  };

  if (isLoading) {
    return (
      <div className="max-w-6xl mx-auto py-12 px-4">
        <div className="bg-white rounded-xl shadow-lg p-8 text-center">
          <MapPin className="h-16 w-16 text-indigo-600 mx-auto mb-4 animate-pulse" />
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Loading Your Roadmap</h2>
          <p className="text-gray-600">Please wait while we prepare your learning journey...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto py-8 px-4">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          {learningPathData ? `Learning Path: ${learningPathData.career.title}` : 'Your Learning Roadmap'}
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          {learningPathData 
            ? `Personalized learning path with progress tracking and checkmarks`
            : 'Follow personalized learning paths designed to help you achieve your career goals'
          }
        </p>
        {learningPathData && (
          <div className="mt-4 flex justify-center space-x-6 text-sm text-gray-600">
            <div className="flex items-center">
              <Target className="h-4 w-4 mr-1" />
              <span>{learningPathData.skills_to_develop.length} skills to develop</span>
            </div>
            <div className="flex items-center">
              <CheckCircle className="h-4 w-4 mr-1 text-green-500" />
              <span>{learningPathData.matching_skills.length} current skills</span>
            </div>
          </div>
        )}
      </div>

      {/* Career Selection */}
      {roadmapData?.roadmaps && roadmapData.roadmaps.length > 0 && (
        <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Select Career Path</h2>
          <div className="grid md:grid-cols-3 gap-4">
            {roadmapData.roadmaps.map((roadmap, index) => (
              <div
                key={index}
                onClick={() => setSelectedCareer(roadmap)}
                className={`border-2 rounded-lg p-4 cursor-pointer transition-all ${
                  selectedCareer?.id === roadmap.id
                    ? 'border-indigo-500 bg-indigo-50'
                    : 'border-gray-200 hover:border-indigo-300'
                }`}
              >
                <h3 className="font-semibold text-gray-900 mb-2">{roadmap.career_path}</h3>
                <p className="text-sm text-gray-600 mb-3">{roadmap.description}</p>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-500">
                    {roadmap.phases?.length || 0} phases
                  </span>
                  <span className="text-gray-500">
                    {roadmap.timeline_months} months
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {selectedCareer ? (
        <div className="space-y-8">
          {/* Roadmap Overview */}
          <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-xl p-8 text-white">
            <div className="text-center">
              <h2 className="text-2xl font-bold mb-4">{selectedCareer.career_path}</h2>
              <p className="text-xl opacity-90 mb-6">{selectedCareer.description}</p>
              <div className="flex justify-center space-x-8 text-sm">
                <div className="flex items-center">
                  <Clock className="h-4 w-4 mr-1" />
                  <span>{selectedCareer.timeline_months} months</span>
                </div>
                <div className="flex items-center">
                  <Target className="h-4 w-4 mr-1" />
                  <span>{selectedCareer.phases?.length || 0} phases</span>
                </div>
                <div className="flex items-center">
                  <BookOpen className="h-4 w-4 mr-1" />
                  <span>{selectedCareer.total_steps || 0} steps</span>
                </div>
              </div>
            </div>
          </div>

          {/* Progress Overview */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl font-bold text-gray-900">Progress Overview</h3>
              <button className="flex items-center px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors text-sm">
                <Download className="h-4 w-4 mr-2" />
                Export Roadmap
              </button>
            </div>

            <div className="grid md:grid-cols-4 gap-4 mb-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-indigo-600">
                  {selectedCareer.phases?.length || 0}
                </div>
                <div className="text-sm text-gray-600">Total Phases</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {selectedCareer.progress?.completed_steps || 0}
                </div>
                <div className="text-sm text-gray-600">Steps Completed</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">
                  {selectedCareer.progress?.total_steps || selectedCareer.total_steps || 0}
                </div>
                <div className="text-sm text-gray-600">Total Steps</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600">
                  {Math.round(selectedCareer.progress?.overall_progress || 0)}%
                </div>
                <div className="text-sm text-gray-600">Overall Progress</div>
              </div>
            </div>

            <div className="w-full bg-gray-200 rounded-full h-3">
              <div
                className="bg-gradient-to-r from-indigo-500 to-purple-600 h-3 rounded-full transition-all duration-300"
                style={{ width: `${selectedCareer.progress?.overall_progress || 0}%` }}
              ></div>
            </div>
          </div>

          {/* Learning Phases with Checkboxes */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h3 className="text-xl font-bold text-gray-900 mb-6">Learning Phases</h3>
            
            <div className="space-y-6">
              {selectedCareer.phases?.map((phase, phaseIndex) => (
                <div key={phaseIndex} className="border border-gray-200 rounded-lg overflow-hidden">
                  <div
                    className={`p-6 cursor-pointer transition-colors ${
                      activePhase === phaseIndex ? 'bg-indigo-50 border-b border-gray-200' : 'hover:bg-gray-50'
                    }`}
                    onClick={() => setActivePhase(activePhase === phaseIndex ? -1 : phaseIndex)}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                          phase.steps?.every(step => step.is_completed)
                            ? 'bg-green-100 text-green-600' 
                            : phase.steps?.some(step => step.is_completed)
                            ? 'bg-indigo-100 text-indigo-600'
                            : 'bg-gray-100 text-gray-600'
                        }`}>
                          {phase.steps?.every(step => step.is_completed) ? (
                            <CheckCircle className="h-5 w-5" />
                          ) : (
                            phaseIndex + 1
                          )}
                        </div>
                        <div className="ml-4">
                          <h4 className="text-lg font-semibold text-gray-900">{phase.title}</h4>
                          <p className="text-gray-600">{phase.description}</p>
                          <div className="mt-1 text-sm text-gray-500">
                            {phase.steps?.filter(step => step.is_completed).length || 0} of {phase.steps?.length || 0} steps completed
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-4">
                        <div className="text-sm text-gray-500">
                          {phase.estimated_duration_weeks} weeks
                        </div>
                        <ArrowRight className={`h-5 w-5 transition-transform ${
                          activePhase === phaseIndex ? 'rotate-90' : ''
                        }`} />
                      </div>
                    </div>
                  </div>

                  {activePhase === phaseIndex && (
                    <div className="p-6 bg-gray-50">
                      <div className="space-y-4">
                        <h5 className="font-semibold text-gray-900 mb-4 flex items-center">
                          <Target className="h-4 w-4 mr-2" />
                          Learning Steps
                        </h5>
                        
                        {phase.steps?.map((step, stepIndex) => (
                          <div key={stepIndex} className="border border-gray-200 rounded-lg p-4 bg-white">
                            <div className="flex items-start space-x-3">
                              {/* Checkbox */}
                              <button
                                onClick={() => updateStepProgress(
                                  selectedCareer.id, 
                                  phase.phase_id, 
                                  step.step_id, 
                                  !step.is_completed
                                )}
                                className={`flex-shrink-0 w-5 h-5 rounded border-2 flex items-center justify-center transition-colors ${
                                  step.is_completed
                                    ? 'bg-green-500 border-green-500 text-white'
                                    : 'border-gray-300 hover:border-indigo-500'
                                }`}
                              >
                                {step.is_completed && <Check className="h-3 w-3" />}
                              </button>
                              
                              {/* Step Content */}
                              <div className="flex-1">
                                <div className="flex items-start justify-between">
                                  <div>
                                    <h6 className={`font-medium ${
                                      step.is_completed ? 'text-green-700 line-through' : 'text-gray-900'
                                    }`}>
                                      {step.title}
                                    </h6>
                                    <p className="text-sm text-gray-600 mt-1">
                                      {step.description}
                                    </p>
                                    <div className="flex items-center mt-2 space-x-4">
                                      <span className="text-xs text-gray-500 capitalize">
                                        {step.step_type}
                                      </span>
                                      <span className="text-xs text-gray-500">
                                        {step.estimated_hours}h
                                      </span>
                                      <span className="text-xs text-gray-500 capitalize">
                                        {step.difficulty_level}
                                      </span>
                                      {step.completed_at && (
                                        <span className="text-xs text-green-600">
                                          ✓ Completed {new Date(step.completed_at).toLocaleDateString()}
                                        </span>
                                      )}
                                    </div>
                                  </div>
                                </div>
                                
                                {/* Resources */}
                                {step.resources && step.resources.length > 0 && (
                                  <div className="mt-3 space-y-2">
                                    <div className="text-xs font-medium text-gray-700">Resources:</div>
                                    {step.resources.map((resource, resourceIndex) => (
                                      <div key={resourceIndex} className="flex items-center justify-between text-xs">
                                        <div className="flex items-center space-x-2">
                                          <span className="text-gray-600">{resource.title}</span>
                                          <span className="text-gray-500">({resource.type})</span>
                                        </div>
                                        <button className="text-indigo-600 hover:text-indigo-800">
                                          <ExternalLink className="h-3 w-3" />
                                        </button>
                                      </div>
                                    ))}
                                  </div>
                                )}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Completion Celebration */}
          {selectedCareer.progress?.overall_progress === 100 && (
            <div className="bg-gradient-to-r from-green-500 to-emerald-600 rounded-xl p-8 text-white text-center">
              <Award className="h-16 w-16 mx-auto mb-4" />
              <h3 className="text-2xl font-bold mb-2">Congratulations! 🎉</h3>
              <p className="text-xl opacity-90 mb-6">
                You've completed your {selectedCareer.career_path} learning roadmap!
              </p>
              <div className="space-x-4">
                <button className="px-6 py-3 bg-white text-green-600 rounded-lg font-medium hover:bg-green-50 transition-colors">
                  Download Certificate
                </button>
                <button className="px-6 py-3 border border-white text-white rounded-lg font-medium hover:bg-white hover:text-green-600 transition-colors">
                  Share Achievement
                </button>
              </div>
            </div>
          )}

          {/* Next Steps */}
          <div className="bg-white rounded-xl shadow-lg p-8">
            <h3 className="text-xl font-bold text-gray-900 mb-6 text-center">Accelerate Your Learning</h3>
            <div className="grid md:grid-cols-3 gap-6">
              <div className="text-center">
                <Users className="h-12 w-12 text-indigo-600 mx-auto mb-4" />
                <h4 className="font-semibold text-gray-900 mb-2">Join Study Groups</h4>
                <p className="text-gray-600 text-sm mb-4">
                  Connect with peers on similar learning paths
                </p>
                <button className="text-indigo-600 font-medium hover:text-indigo-800">
                  Find Groups →
                </button>
              </div>

              <div className="text-center">
                <Award className="h-12 w-12 text-green-600 mx-auto mb-4" />
                <h4 className="font-semibold text-gray-900 mb-2">Earn Certificates</h4>
                <p className="text-gray-600 text-sm mb-4">
                  Complete courses and showcase your achievements
                </p>
                <button className="text-green-600 font-medium hover:text-green-800">
                  View Certificates →
                </button>
              </div>

              <div className="text-center">
                <Calendar className="h-12 w-12 text-purple-600 mx-auto mb-4" />
                <h4 className="font-semibold text-gray-900 mb-2">Set Schedule</h4>
                <p className="text-gray-600 text-sm mb-4">
                  Create a consistent learning routine
                </p>
                <button className="text-purple-600 font-medium hover:text-purple-800">
                  Schedule Learning →
                </button>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="bg-white rounded-xl shadow-lg p-12 text-center">
          <MapPin className="h-16 w-16 text-gray-400 mx-auto mb-6" />
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Create Your First Roadmap</h2>
          <p className="text-gray-600 mb-8 max-w-md mx-auto">
            Complete a career assessment to get personalized learning roadmaps with progress tracking
          </p>
          <div className="space-y-4">
            <button
              onClick={() => navigate('/')}
              className="px-8 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
            >
              Take Assessment
            </button>
          </div>
        </div>
      )}

      {/* Career Selection */}
      {roadmapData?.roadmaps && roadmapData.roadmaps.length > 0 && (
        <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Select Career Path</h2>
          <div className="grid md:grid-cols-3 gap-4">
            {roadmapData.roadmaps.map((roadmap, index) => (
              <div
                key={index}
                onClick={() => setSelectedCareer(roadmap)}
                className={`border-2 rounded-lg p-4 cursor-pointer transition-all ${
                  selectedCareer?.id === roadmap.id
                    ? 'border-indigo-500 bg-indigo-50'
                    : 'border-gray-200 hover:border-indigo-300'
                }`}
              >
                <h3 className="font-semibold text-gray-900 mb-2">{roadmap.career_path}</h3>
                <p className="text-sm text-gray-600 mb-3">{roadmap.description}</p>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-500">
                    {roadmap.phases?.length || 0} phases
                  </span>
                  <span className="text-gray-500">
                    {roadmap.timeline_months} months
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {selectedCareer ? (
        <div className="space-y-8">
          {/* Roadmap Overview */}
          <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-xl p-8 text-white">
            <div className="text-center">
              <h2 className="text-2xl font-bold mb-4">{selectedCareer.career_path}</h2>
              <p className="text-xl opacity-90 mb-6">{selectedCareer.description}</p>
              <div className="flex justify-center space-x-8 text-sm">
                <div className="flex items-center">
                  <Clock className="h-4 w-4 mr-1" />
                  <span>{selectedCareer.timeline_months} months</span>
                </div>
                <div className="flex items-center">
                  <Target className="h-4 w-4 mr-1" />
                  <span>{selectedCareer.phases?.length || 0} phases</span>
                </div>
                <div className="flex items-center">
                  <BookOpen className="h-4 w-4 mr-1" />
                  <span>{selectedCareer.total_resources || 0} resources</span>
                </div>
              </div>
            </div>
          </div>

          {/* Progress Overview */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl font-bold text-gray-900">Progress Overview</h3>
              <button className="flex items-center px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors text-sm">
                <Download className="h-4 w-4 mr-2" />
                Export Roadmap
              </button>
            </div>

            <div className="grid md:grid-cols-4 gap-4 mb-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-indigo-600">
                  {selectedCareer.progress?.completed_phases || 0}
                </div>
                <div className="text-sm text-gray-600">Phases Completed</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {selectedCareer.progress?.completed_milestones || 0}
                </div>
                <div className="text-sm text-gray-600">Milestones Achieved</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">
                  {selectedCareer.progress?.hours_spent || 0}h
                </div>
                <div className="text-sm text-gray-600">Time Invested</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600">
                  {selectedCareer.progress?.overall_progress || 0}%
                </div>
                <div className="text-sm text-gray-600">Overall Progress</div>
              </div>
            </div>

            <div className="w-full bg-gray-200 rounded-full h-3">
              <div
                className="bg-gradient-to-r from-indigo-500 to-purple-600 h-3 rounded-full"
                style={{ width: `${selectedCareer.progress?.overall_progress || 0}%` }}
              ></div>
            </div>
          </div>

          {/* Learning Phases */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h3 className="text-xl font-bold text-gray-900 mb-6">Learning Phases</h3>
            
            <div className="space-y-6">
              {selectedCareer.phases?.map((phase, index) => (
                <div key={index} className="border border-gray-200 rounded-lg overflow-hidden">
                  <div
                    className={`p-6 cursor-pointer transition-colors ${
                      activePhase === index ? 'bg-indigo-50 border-b border-gray-200' : 'hover:bg-gray-50'
                    }`}
                    onClick={() => setActivePhase(activePhase === index ? -1 : index)}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                          phase.status === 'completed' 
                            ? 'bg-green-100 text-green-600' 
                            : phase.status === 'in_progress'
                            ? 'bg-indigo-100 text-indigo-600'
                            : 'bg-gray-100 text-gray-600'
                        }`}>
                          {phase.status === 'completed' ? (
                            <CheckCircle className="h-5 w-5" />
                          ) : (
                            index + 1
                          )}
                        </div>
                        <div className="ml-4">
                          <h4 className="text-lg font-semibold text-gray-900">{phase.title}</h4>
                          <p className="text-gray-600">{phase.description}</p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-4">
                        <div className="text-sm text-gray-500">
                          {phase.duration_weeks} weeks
                        </div>
                        <ArrowRight className={`h-5 w-5 transition-transform ${
                          activePhase === index ? 'rotate-90' : ''
                        }`} />
                      </div>
                    </div>
                  </div>

                  {activePhase === index && (
                    <div className="p-6 bg-gray-50">
                      <div className="grid md:grid-cols-2 gap-6">
                        {/* Milestones */}
                        <div>
                          <h5 className="font-semibold text-gray-900 mb-3 flex items-center">
                            <Target className="h-4 w-4 mr-2" />
                            Milestones
                          </h5>
                          <div className="space-y-2">
                            {phase.milestones?.map((milestone, mIndex) => (
                              <div key={mIndex} className="flex items-center">
                                <div className={`w-4 h-4 rounded-full mr-3 ${
                                  milestone.completed 
                                    ? 'bg-green-500' 
                                    : 'bg-gray-300'
                                }`}></div>
                                <span className={`text-sm ${
                                  milestone.completed 
                                    ? 'text-green-700 line-through' 
                                    : 'text-gray-700'
                                }`}>
                                  {milestone.title}
                                </span>
                              </div>
                            ))}
                          </div>
                        </div>

                        {/* Resources */}
                        <div>
                          <h5 className="font-semibold text-gray-900 mb-3 flex items-center">
                            <BookOpen className="h-4 w-4 mr-2" />
                            Learning Resources
                          </h5>
                          <div className="space-y-3">
                            {phase.resources?.map((resource, rIndex) => (
                              <div key={rIndex} className="border border-gray-200 rounded-lg p-3">
                                <div className="flex items-start justify-between">
                                  <div className="flex-1">
                                    <h6 className="font-medium text-gray-900">{resource.title}</h6>
                                    <p className="text-sm text-gray-600">{resource.description}</p>
                                    <div className="flex items-center mt-2 space-x-4">
                                      <span className="text-xs text-gray-500 capitalize">
                                        {resource.type}
                                      </span>
                                      <span className="text-xs text-gray-500">
                                        {resource.duration}
                                      </span>
                                      {resource.rating && (
                                        <div className="flex items-center">
                                          <Star className="h-3 w-3 text-yellow-400 fill-current" />
                                          <span className="text-xs text-gray-500 ml-1">
                                            {resource.rating}
                                          </span>
                                        </div>
                                      )}
                                    </div>
                                  </div>
                                  <div className="flex space-x-2 ml-4">
                                    {resource.completed ? (
                                      <CheckCircle className="h-5 w-5 text-green-500" />
                                    ) : (
                                      <button className="p-1 text-indigo-600 hover:text-indigo-800">
                                        <Play className="h-4 w-4" />
                                      </button>
                                    )}
                                    <button className="p-1 text-gray-400 hover:text-gray-600">
                                      <ExternalLink className="h-4 w-4" />
                                    </button>
                                  </div>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>

                      {/* Phase Actions */}
                      <div className="mt-6 flex justify-between items-center">
                        <div className="text-sm text-gray-600">
                          Progress: {phase.completion_percentage || 0}% complete
                        </div>
                        <div className="space-x-3">
                          {phase.status === 'not_started' && (
                            <button 
                              onClick={() => startPhase(index)}
                              className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors text-sm"
                            >
                              Start Phase
                            </button>
                          )}
                          {phase.status === 'in_progress' && (
                            <button className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm">
                              Continue Learning
                            </button>
                          )}
                          <button className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors text-sm">
                            View Details
                          </button>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Next Steps */}
          <div className="bg-white rounded-xl shadow-lg p-8">
            <h3 className="text-xl font-bold text-gray-900 mb-6 text-center">Accelerate Your Learning</h3>
            <div className="grid md:grid-cols-3 gap-6">
              <div className="text-center">
                <Users className="h-12 w-12 text-indigo-600 mx-auto mb-4" />
                <h4 className="font-semibold text-gray-900 mb-2">Join Study Groups</h4>
                <p className="text-gray-600 text-sm mb-4">
                  Connect with peers on similar learning paths
                </p>
                <button className="text-indigo-600 font-medium hover:text-indigo-800">
                  Find Groups →
                </button>
              </div>

              <div className="text-center">
                <Award className="h-12 w-12 text-green-600 mx-auto mb-4" />
                <h4 className="font-semibold text-gray-900 mb-2">Earn Certificates</h4>
                <p className="text-gray-600 text-sm mb-4">
                  Complete courses and showcase your achievements
                </p>
                <button className="text-green-600 font-medium hover:text-green-800">
                  View Certificates →
                </button>
              </div>

              <div className="text-center">
                <Calendar className="h-12 w-12 text-purple-600 mx-auto mb-4" />
                <h4 className="font-semibold text-gray-900 mb-2">Set Schedule</h4>
                <p className="text-gray-600 text-sm mb-4">
                  Create a consistent learning routine
                </p>
                <button className="text-purple-600 font-medium hover:text-purple-800">
                  Schedule Learning →
                </button>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="bg-white rounded-xl shadow-lg p-12 text-center">
          <MapPin className="h-16 w-16 text-gray-400 mx-auto mb-6" />
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Create Your First Roadmap</h2>
          <p className="text-gray-600 mb-8 max-w-md mx-auto">
            Complete a career assessment to get personalized learning roadmaps for your chosen career path
          </p>
          <div className="space-y-4">
            <button
              onClick={() => navigate('/')}
              className="px-8 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
            >
              Take Assessment
            </button>
            <div className="text-sm text-gray-500">or</div>
            <button
              onClick={() => createNewRoadmap('Software Engineer')}
              className="px-8 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Create Sample Roadmap
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default CareerRoadmap;
