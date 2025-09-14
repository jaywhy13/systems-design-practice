import React, { useState, useEffect } from 'react';
import './CompletedInterview.css';

const CompletedInterview = ({ interview, onBack }) => {
  const [selectedArticle, setSelectedArticle] = useState(null);
  const [articleChat, setArticleChat] = useState(null);
  const [chatInput, setChatInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isRecommendationsExpanded, setIsRecommendationsExpanded] = useState(false);

  const API_BASE_URL = 'http://localhost:8000/api/interview';

  const startArticleChat = async (article) => {
    try {
      const response = await fetch(`${API_BASE_URL}/${interview.id}/articles/${article.id}/chat/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        const chatData = await response.json();
        setArticleChat(chatData);
        setSelectedArticle(article);
      }
    } catch (error) {
      console.error('Error starting article chat:', error);
    }
  };

  const sendArticleMessage = async (e) => {
    e.preventDefault();
    if (!chatInput.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: chatInput.trim(),
      timestamp: new Date().toISOString()
    };

    setArticleChat(prev => ({
      ...prev,
      messages: [...prev.messages, userMessage]
    }));
    setChatInput('');
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/article-chat/${articleChat.id}/send/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ content: userMessage.content }),
      });

      if (response.ok) {
        const data = await response.json();
        setArticleChat(prev => ({
          ...prev,
          messages: [...prev.messages, data.ai_response]
        }));
      } else {
        throw new Error('Failed to send message');
      }
    } catch (error) {
      console.error('Error sending article message:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  const getSourceIcon = (source) => {
    switch (source) {
      case 'shopify':
        return '🛍️';
      case 'robinhood':
        return '📈';
      case 'pinterest':
        return '📌';
      default:
        return '📄';
    }
  };

  if (selectedArticle && articleChat) {
    return (
      <div className="completed-interview">
        <div className="article-chat-header">
          <button className="back-btn" onClick={() => setSelectedArticle(null)}>
            ← Back to Articles
          </button>
          <div className="article-info">
            <h2>{selectedArticle.title}</h2>
            <p className="article-source">
              {getSourceIcon(selectedArticle.source)} {selectedArticle.source}
            </p>
          </div>
        </div>

        <div className="article-summary">
          <h3>Summary</h3>
          <p>{selectedArticle.summary}</p>
          
          <h3>Key Highlights</h3>
          <ul>
            {selectedArticle.key_highlights.map((highlight, index) => (
              <li key={index}>{highlight}</li>
            ))}
          </ul>
          
          <a 
            href={selectedArticle.url} 
            target="_blank" 
            rel="noopener noreferrer"
            className="read-article-btn"
          >
            Read Full Article
          </a>
        </div>

        <div className="article-chat-section">
          <h3>Discuss This Article</h3>
          <div className="chat-messages">
            {articleChat.messages.map((message) => (
              <div
                key={message.id}
                className={`message ${message.role === 'user' ? 'user-message' : 'assistant-message'}`}
              >
                <div className="message-content">
                  <div className="message-text">{message.content}</div>
                  <div className="message-time">{formatTime(message.timestamp)}</div>
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="message assistant-message">
                <div className="message-content">
                  <div className="message-text">
                    <div className="typing-indicator">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>

          <form onSubmit={sendArticleMessage} className="chat-input-form">
            <div className="chat-input-container">
              <textarea
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                placeholder="Ask questions about this article..."
                rows="1"
                disabled={isLoading}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    sendArticleMessage(e);
                  }
                }}
              />
              <button
                type="submit"
                disabled={!chatInput.trim() || isLoading}
                className="send-btn"
              >
                Send
              </button>
            </div>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="completed-interview">
      <div className="interview-header">
        <button className="back-btn" onClick={onBack}>
          ← Back to Interviews
        </button>
        <div className="interview-info">
          <h2>{interview.question}</h2>
          <p className="interview-date">
            Completed on {formatDate(interview.created_at)}
          </p>
        </div>
      </div>

      <div className="interview-content">
        <div className="conversation-section">
          <h3>Interview Conversation</h3>
          <div className="conversation-messages">
            {interview.messages.map((message) => (
              <div
                key={message.id}
                className={`message ${message.role === 'user' ? 'user-message' : 'assistant-message'}`}
              >
                <div className="message-content">
                  <div className="message-text">{message.content}</div>
                  {message.images && message.images.length > 0 && (
                    <div className="message-images">
                      {message.images.map((image, index) => (
                        <div key={index} className="message-image">
                          <img 
                            src={image.image} 
                            alt={`Uploaded image ${index + 1}`}
                            onClick={() => window.open(image.image, '_blank')}
                          />
                        </div>
                      ))}
                    </div>
                  )}
                  <div className="message-time">{formatTime(message.timestamp)}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="recommendations-section">
          <div 
            className="recommendations-header"
            onClick={() => setIsRecommendationsExpanded(!isRecommendationsExpanded)}
          >
            <div className="recommendations-title">
              <h3>Recommended Articles</h3>
              <span className="article-count">
                {interview.recommended_articles.length} articles
              </span>
            </div>
            <div className={`expand-icon ${isRecommendationsExpanded ? 'expanded' : ''}`}>
              ▼
            </div>
          </div>
          
          {isRecommendationsExpanded && (
            <div className="recommendations-content">
              <p className="recommendations-intro">
                Based on your interview discussion, here are some relevant articles to deepen your understanding:
              </p>
              
              <div className="articles-grid">
                {interview.recommended_articles.map((rec) => (
                  <div key={rec.id} className="article-card">
                    <div className="article-header">
                      <span className="article-source-icon">
                        {getSourceIcon(rec.article.source)}
                      </span>
                      <span className="article-source">{rec.article.source}</span>
                    </div>
                    
                    <h4 className="article-title">{rec.article.title}</h4>
                    
                    <p className="article-summary-text">
                      {rec.article.summary}
                    </p>
                    
                    <div className="article-highlights">
                      <strong>Key Points:</strong>
                      <ul>
                        {rec.article.key_highlights.slice(0, 3).map((highlight, index) => (
                          <li key={index}>{highlight}</li>
                        ))}
                      </ul>
                    </div>
                    
                    <div className="article-actions">
                      <button
                        className="discuss-btn"
                        onClick={() => startArticleChat(rec.article)}
                      >
                        Discuss Article
                      </button>
                      <a
                        href={rec.article.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="read-btn"
                      >
                        Read Article
                      </a>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CompletedInterview;
