import React, { useState, useEffect } from 'react';
import './App.css';
import InterviewList from './components/InterviewList';
import InterviewChat from './components/InterviewChat';
import StartInterview from './components/StartInterview';
import CompletedInterview from './components/CompletedInterview';

function App() {
  const [currentView, setCurrentView] = useState('list'); // 'list', 'chat', 'start', 'completed'
  const [currentInterview, setCurrentInterview] = useState(null);
  const [interviews, setInterviews] = useState([]);

  const API_BASE_URL = "http://13.222.86.82:8000/api/interview";

  useEffect(() => {
    fetchInterviews();
  }, []);

  const fetchInterviews = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/list/`);
      const data = await response.json();
      setInterviews(data);
    } catch (error) {
      console.error('Error fetching interviews:', error);
    }
  };

  const startNewInterview = async (question) => {
    try {
      const response = await fetch(`${API_BASE_URL}/start/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question }),
      });
      const interview = await response.json();
      setCurrentInterview(interview);
      setCurrentView('chat');
      fetchInterviews(); // Refresh the list
    } catch (error) {
      console.error('Error starting interview:', error);
    }
  };

  const endInterview = async (interviewId) => {
    try {
      await fetch(`${API_BASE_URL}/${interviewId}/end/`, {
        method: 'POST',
      });
      setCurrentInterview(null);
      setCurrentView('list');
      fetchInterviews(); // Refresh the list
    } catch (error) {
      console.error('Error ending interview:', error);
    }
  };

  const openInterview = (interview) => {
    setCurrentInterview(interview);
    if (interview.is_active) {
      setCurrentView('chat');
    } else {
      setCurrentView('completed');
    }
  };

  const renderCurrentView = () => {
    switch (currentView) {
      case 'start':
        return (
          <StartInterview
            onStart={startNewInterview}
            onBack={() => setCurrentView('list')}
          />
        );
      case 'chat':
        return (
          <InterviewChat
            interview={currentInterview}
            onEnd={endInterview}
            onBack={() => setCurrentView('list')}
            apiBaseUrl={API_BASE_URL}
          />
        );
      case 'completed':
        return (
          <CompletedInterview
            interview={currentInterview}
            onBack={() => setCurrentView('list')}
          />
        );
      default:
        return (
          <InterviewList
            interviews={interviews}
            onStartNew={() => setCurrentView('start')}
            onOpenInterview={openInterview}
          />
        );
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>System Design Interview Practice</h1>
      </header>
      <main className="App-main">
        {renderCurrentView()}
      </main>
    </div>
  );
}

export default App;
