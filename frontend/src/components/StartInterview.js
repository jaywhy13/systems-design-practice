import React, { useState } from 'react';
import './StartInterview.css';

const StartInterview = ({ onStart, onBack }) => {
  const [question, setQuestion] = useState('');
  const [selectedPreset, setSelectedPreset] = useState('');

  const presetQuestions = [
    'Design YouTube',
    'Build a URL shortener',
    'Create a global code deployment system',
    'Design a chat application',
    'Build a ride-sharing service',
    'Design a social media platform',
    'Create a recommendation system',
    'Build a payment processing system',
    'Design a search engine',
    'Create a content delivery network'
  ];

  const handlePresetSelect = (preset) => {
    setSelectedPreset(preset);
    setQuestion(preset);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (question.trim()) {
      onStart(question.trim());
    }
  };

  return (
    <div className="start-interview">
      <div className="start-interview-header">
        <button className="back-btn" onClick={onBack}>
          ← Back to Interviews
        </button>
        <h2>Start New Interview</h2>
      </div>

      <div className="start-interview-content">
        <form onSubmit={handleSubmit} className="interview-form">
          <div className="form-group">
            <label htmlFor="question">System Design Question:</label>
            <textarea
              id="question"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Enter your system design question or select from presets below..."
              rows="4"
              required
            />
          </div>

          <div className="preset-questions">
            <h3>Or choose from popular questions:</h3>
            <div className="preset-grid">
              {presetQuestions.map((preset) => (
                <button
                  key={preset}
                  type="button"
                  className={`preset-btn ${selectedPreset === preset ? 'selected' : ''}`}
                  onClick={() => handlePresetSelect(preset)}
                >
                  {preset}
                </button>
              ))}
            </div>
          </div>

          <div className="form-actions">
            <button type="submit" className="start-btn" disabled={!question.trim()}>
              Start Interview
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default StartInterview;
