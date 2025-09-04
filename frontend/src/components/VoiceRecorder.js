import React, { useState, useRef, useEffect } from 'react';
import { Mic, Square, CheckCircle, X, RotateCcw } from 'lucide-react';

const VoiceRecorder = ({ onRecordingComplete, onError, buttonText = 'Record Answer', questionIndex }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  // Store recordings in a map by question index
  const [recordings, setRecordings] = useState({});
  
  // Get the current recording for this question
  const currentRecording = recordings[questionIndex] || {};
  const audioBlob = currentRecording.blob;
  const audioUrl = currentRecording.url || '';
  const [recordingTime, setRecordingTime] = useState(0);
  const mediaRecorderRef = useRef(null);
  const timerRef = useRef(null);

  // Clean up resources when component unmounts
  useEffect(() => {
    return () => {
      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
        mediaRecorderRef.current.stop();
      }
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, []);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      const audioChunks = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunks.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
        const audioUrl = URL.createObjectURL(audioBlob);
        
        setRecordings(prev => ({
          ...prev,
          [questionIndex]: { blob: audioBlob, url: audioUrl }
        }));
        
        setIsProcessing(false);
      };

      mediaRecorder.start();
      setIsRecording(true);
      setRecordingTime(0);
      
      // Start timer
      timerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);
      
    } catch (err) {
      console.error('Error accessing microphone:', err);
      onError?.('Could not access microphone. Please check permissions.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
      clearInterval(timerRef.current);
      setIsRecording(false);
      setIsProcessing(true);
    }
  };

  const handleSubmit = async () => {
    if (!audioBlob) return;
    
    try {
      setIsProcessing(true);
      const formData = new FormData();
      formData.append('audio', audioBlob, 'recording.wav');
      
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/voice/transcribe`, {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        throw new Error('Failed to transcribe audio');
      }
      
      const result = await response.json();
      onRecordingComplete?.(result.text);
      
    } catch (err) {
      console.error('Error transcribing audio:', err);
      onError?.('Failed to transcribe audio. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  const resetRecording = () => {
    setRecordings(prev => {
      const newRecordings = { ...prev };
      delete newRecordings[questionIndex];
      return newRecordings;
    });
    setRecordingTime(0);
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="space-y-4 w-full">
      {!audioUrl ? (
        <button
          onClick={isRecording ? stopRecording : startRecording}
          disabled={isProcessing}
          className={`flex items-center justify-center w-full px-6 py-3 text-base font-medium rounded-lg text-white transition-colors ${
            isRecording
              ? 'bg-red-600 hover:bg-red-700 animate-pulse'
              : 'bg-blue-600 hover:bg-blue-700'
          } focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50`}
        >
          {isRecording ? (
            <>
              <div className="flex items-center">
                <div className="w-3 h-3 bg-white rounded-full mr-2 animate-ping" />
                <Square className="w-5 h-5 mr-2" />
                <span>Recording ({formatTime(recordingTime)})</span>
              </div>
            </>
          ) : (
            <>
              <Mic className="w-5 h-5 mr-2" />
              <span className="text-base">{buttonText}</span>
            </>
          )}
        </button>
      ) : (
        <div className="space-y-4">
          <div className="flex flex-col space-y-3">
            <div className="flex items-center justify-between bg-white p-3 rounded-lg border border-gray-200">
              <audio 
                src={audioUrl} 
                controls 
                className="flex-1 mr-2"
                controlsList="nodownload"
              />
              <div className="flex space-x-2">
                <button
                  onClick={resetRecording}
                  className="p-2 text-gray-500 hover:text-red-600 transition-colors rounded-full hover:bg-red-50"
                  title="Retry recording"
                >
                  <RotateCcw className="w-5 h-5" />
                </button>
              </div>
            </div>
            
            <button
              onClick={handleSubmit}
              disabled={isProcessing}
              className="flex items-center justify-center w-full px-6 py-3 text-base font-medium text-white bg-green-600 rounded-lg hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 transition-colors"
            >
              {isProcessing ? (
                <>
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Processing...
                </>
              ) : (
                <>
                  <CheckCircle className="w-5 h-5 mr-2" />
                  <span>Submit Answer</span>
                </>
              )}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default VoiceRecorder;
