import React from 'react';
import './InterviewList.css';

const InterviewList = ({ interviews, onStartNew, onOpenInterview }) => {
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <div className="interview-list">
      <div className="interview-list-header">
        <h2>Your Interviews</h2>
        <button className="start-new-btn" onClick={onStartNew}>
          Start New Interview
        </button>
      </div>
      
      <div className="interviews-container">
        {interviews.length === 0 ? (
          <div className="no-interviews">
            <p>No interviews yet. Start your first one!</p>
          </div>
        ) : (
          interviews.map((interview) => (
            <div key={interview.id} className={`interview-card ${!interview.is_active ? 'completed' : ''}`}>
              <div className="interview-info">
                <h3>{interview.question}</h3>
                <p className="interview-date">
                  Created: {formatDate(interview.created_at)}
                </p>
                <p className="interview-status">
                  Status: {interview.is_active ? 'Active' : 'Completed'}
                </p>
                <p className="message-count">
                  Messages: {interview.messages?.length || 0}
                </p>
              </div>
                             <div className="interview-actions">
                 <button
                   className="open-btn"
                   onClick={() => onOpenInterview(interview)}
                 >
                   {interview.is_active ? 'Continue' : 'View'}
                 </button>
               </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default InterviewList;
