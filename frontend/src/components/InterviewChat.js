import React, { useState, useEffect, useRef } from 'react';
import './InterviewChat.css';

const InterviewChat = ({ interview, onEnd, onBack, apiBaseUrl }) => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedImages, setSelectedImages] = useState([]);
  const [isDragOver, setIsDragOver] = useState(false);
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  useEffect(() => {
    if (interview && interview.messages) {
      setMessages(interview.messages);
    }
  }, [interview]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleImageSelect = (files) => {
    const imageFiles = Array.from(files).filter(file => 
      file.type.startsWith('image/')
    );
    setSelectedImages(prev => [...prev, ...imageFiles]);
  };

  const removeImage = (index) => {
    setSelectedImages(prev => prev.filter((_, i) => i !== index));
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    const files = e.dataTransfer.files;
    handleImageSelect(files);
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if ((!inputMessage.trim() && selectedImages.length === 0) || isLoading) return;

    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: inputMessage.trim(),
      timestamp: new Date().toISOString(),
      images: selectedImages.map(img => ({ url: URL.createObjectURL(img) }))
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const formData = new FormData();
      formData.append('content', inputMessage.trim());
      
      selectedImages.forEach((image, index) => {
        formData.append(`images`, image);
      });

      const response = await fetch(`${apiBaseUrl}/${interview.id}/send/`, {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        setMessages(prev => [...prev, data.ai_response]);
        setSelectedImages([]);
      } else {
        throw new Error('Failed to send message');
      }
    } catch (error) {
      console.error('Error sending message:', error);
      // Add error message to chat
      setMessages(prev => [...prev, {
        id: Date.now(),
        role: 'assistant',
        content: 'Sorry, there was an error processing your message. Please try again.',
        timestamp: new Date().toISOString()
      }]);
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

  return (
    <div className="interview-chat">
      <div className="chat-header">
        <button className="back-btn" onClick={onBack}>
          ← Back to Interviews
        </button>
        <div className="chat-title">
          <h2>{interview.question}</h2>
          <span className="chat-status">
            {interview.is_active ? 'Active' : 'Completed'}
          </span>
        </div>
        {interview.is_active && (
          <button className="end-btn" onClick={() => onEnd(interview.id)}>
            End Interview
          </button>
        )}
      </div>

      <div className="chat-messages">
        {messages.map((message) => (
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
                        src={image.url || image.image} 
                        alt={`Uploaded image ${index + 1}`}
                        onClick={() => window.open(image.url || image.image, '_blank')}
                      />
                    </div>
                  ))}
                </div>
              )}
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
        <div ref={messagesEndRef} />
      </div>

      {interview.is_active && (
        <div className="chat-input-section">
          {selectedImages.length > 0 && (
            <div className="selected-images">
              {selectedImages.map((image, index) => (
                <div key={index} className="selected-image">
                  <img src={URL.createObjectURL(image)} alt={`Selected ${index + 1}`} />
                  <button 
                    className="remove-image-btn"
                    onClick={() => removeImage(index)}
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          )}
          
          <form onSubmit={sendMessage} className="chat-input-form">
            <div className="chat-input-container">
              <textarea
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder="Type your message or drag images here..."
                rows="1"
                disabled={isLoading}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    sendMessage(e);
                  }
                }}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                className={isDragOver ? 'drag-over' : ''}
              />
              <div className="chat-input-actions">
                <button
                  type="button"
                  className="upload-btn"
                  onClick={() => fileInputRef.current?.click()}
                  disabled={isLoading}
                >
                  📷
                </button>
                <button
                  type="submit"
                  disabled={(!inputMessage.trim() && selectedImages.length === 0) || isLoading}
                  className="send-btn"
                >
                  Send
                </button>
              </div>
            </div>
          </form>
          
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept="image/*"
            onChange={(e) => handleImageSelect(e.target.files)}
            style={{ display: 'none' }}
          />
        </div>
      )}
    </div>
  );
};

export default InterviewChat;
