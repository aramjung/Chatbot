import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import './App.css';

// Use environment variable for API URL, fallback to relative path for development proxy
const API_BASE_URL = process.env.REACT_APP_API_URL || '';

function App() {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);  // Reference to the end of messages for auto-scrolling

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Scroll to bottom whenever messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      role: 'user',
      content: inputMessage.trim()
    };

    // Add user message to chat
    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    // Indicate loading state
    setIsLoading(true);

    try {
      // Prepare messages for API (include conversation history)
      const conversationHistory = [...messages, userMessage];

      const response = await axios.post(`${API_BASE_URL}/api/chat`, {
        messages: conversationHistory
      });

      const assistantMessage = {
        role: 'assistant',
        content: response.data.message,
        contextChunks: response.data.context_chunks || []
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        role: 'assistant',
        content: 'Sorry, there was an error processing your request. Please try again.'
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage(e);
    }
  };

  const clearChat = () => {
    setMessages([]);
  };

  return (
    <div className="App">
      <div className="chat-container">
        <div className="chat-header">
          <h1>AI Chatbot</h1>
          <button onClick={clearChat} className="clear-button">
            Clear Chat
          </button>
        </div>

        <div className="messages-container">
          {messages.length === 0 && (
            <div className="welcome-message">
              <h2>Welcome to AI Chatbot!</h2>
              <p>Start a conversation by typing a message below.</p>
            </div>
          )}
          
          {messages.map((message, index) => (
            <div
              key={index}
              className={`message ${message.role === 'user' ? 'user-message' : 'assistant-message'}`}
            >
              <div className="message-content">
                <div className="message-role">
                  {message.role === 'user' ? 'You' : 'AI Assistant'}
                </div>
                <div className="message-text">{message.content}</div>
                {message.contextChunks && message.contextChunks.length > 0 && (
                  <div className="context-sources">
                    <div className="sources-header">📚 Sources:</div>
                    {message.contextChunks.map((chunk, chunkIndex) => (
                      <div key={chunkIndex} className="source-item">
                        <div className="source-heading">
                          {chunk.heading || 'Untitled Section'}
                        </div>
                        <div className="source-file">
                          {chunk.source_file}
                        </div>
                        <div className="source-text">
                          {chunk.text.substring(0, 150)}{chunk.text.length > 150 ? '...' : ''}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="message assistant-message">
              <div className="message-content">
                <div className="message-role">AI Assistant</div>
                <div className="message-text loading">
                  <span className="dot"></span>
                  <span className="dot"></span>
                  <span className="dot"></span>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        <form onSubmit={handleSendMessage} className="input-container">
          <textarea
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message here..."
            className="message-input"
            rows="1"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={!inputMessage.trim() || isLoading}
            className="send-button"
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
}

export default App;
