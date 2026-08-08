import { useState } from 'react';
import { sendChatMessage } from './api';
import './App.css';

export default function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleSubmit(event) {
    event.preventDefault();
    const trimmed = input.trim();
    if (!trimmed || isLoading) return;

    const history = messages;
    const userMessage = { role: 'user', content: trimmed };
    setMessages([...history, userMessage]);
    setInput('');
    setError(null);
    setIsLoading(true);

    try {
      const reply = await sendChatMessage(trimmed, history);
      setMessages([...history, userMessage, { role: 'assistant', content: reply }]);
    } catch (err) {
      setError(err.message || 'Something went wrong. Please try again.');
    } finally {
      setIsLoading(false);
    }
  }

  function handleReset() {
    setMessages([]);
    setError(null);
  }

  return (
    <div className="chat">
      <header className="chat-header">
        <h1>Cadre AI Chatbot</h1>
        <button type="button" onClick={handleReset} disabled={messages.length === 0}>
          Clear conversation
        </button>
      </header>

      <div className="chat-messages">
        {messages.length === 0 && (
          <p className="chat-empty">Ask me anything to get started.</p>
        )}
        {messages.map((message, index) => (
          <div key={index} className={`chat-message chat-message--${message.role}`}>
            {message.content}
          </div>
        ))}
        {isLoading && <div className="chat-message chat-message--assistant chat-message--pending">Thinking…</div>}
      </div>

      {error && <div className="chat-error">{error}</div>}

      <form className="chat-input" onSubmit={handleSubmit}>
        <input
          type="text"
          value={input}
          onChange={(event) => setInput(event.target.value)}
          placeholder="Type a message…"
          disabled={isLoading}
        />
        <button type="submit" disabled={isLoading || !input.trim()}>
          Send
        </button>
      </form>
    </div>
  );
}
