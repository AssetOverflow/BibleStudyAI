/** @format */

import React, { useState } from "react";

interface Message {
  id: string;
  type: "user" | "chuck" | "specialist";
  content: string;
  timestamp: Date;
  specialist?: string;
  sources?: string[];
}

const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      type: "chuck",
      content:
        "Hello! I'm Chuck Missler AI. I'm here to help you study the Bible with the same depth and insight that Chuck Missler brought to his teachings. I have access to my team of specialists in prophecy, biblical scholarship, and apologetics. What would you like to explore today?",
      timestamp: new Date(),
      sources: ["Chuck Missler Teaching Archive", "Biblical Database"],
    },
  ]);
  const [newMessage, setNewMessage] = useState("");
  const [isTyping, setIsTyping] = useState(false);

  const handleSendMessage = async () => {
    if (!newMessage.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: "user",
      content: newMessage,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setNewMessage("");
    setIsTyping(true);

    // Simulate Chuck Missler's response with specialist routing
    setTimeout(() => {
      const responses = [
        {
          content:
            "Let me analyze this question... I'm consulting with my prophecy specialist about the timeline implications.",
          specialist: "Prophecy Specialist",
          sources: [
            "Daniel Commentary",
            "Revelation Analysis",
            "Prophetic Timeline Database",
          ],
        },
        {
          content:
            "I'm checking the original Hebrew and Greek texts with my biblical scholar to ensure accuracy.",
          specialist: "Biblical Scholar",
          sources: [
            "Hebrew-Greek Database",
            "Ancient Manuscripts",
            "Lexicon References",
          ],
        },
        {
          content:
            "My apologetics expert is reviewing the philosophical and theological implications of your question.",
          specialist: "Apologetics Expert",
          sources: [
            "Theological Library",
            "Historical Documents",
            "Philosophical Frameworks",
          ],
        },
      ];

      const randomResponse =
        responses[Math.floor(Math.random() * responses.length)];

      const chuckResponse: Message = {
        id: (Date.now() + 1).toString(),
        type: "chuck",
        content: `${randomResponse.content} Based on my analysis and consultation with my team, here's what I can tell you about your question...`,
        timestamp: new Date(),
        specialist: randomResponse.specialist,
        sources: randomResponse.sources,
      };

      setMessages((prev) => [...prev, chuckResponse]);
      setIsTyping(false);
    }, 2000);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className='chat-interface'>
      <div className='messages-container'>
        {messages.map((message) => (
          <div key={message.id} className={`message ${message.type}`}>
            <div className='message-header'>
              <span className='sender'>
                {message.type === "chuck" ? "🎓 Chuck Missler AI" : "👤 You"}
              </span>
              <span className='timestamp'>
                {message.timestamp.toLocaleTimeString([], {
                  hour: "2-digit",
                  minute: "2-digit",
                })}
              </span>
            </div>
            <div className='message-content'>{message.content}</div>
            {message.specialist && (
              <div className='specialist-badge'>
                🔬 Consulted: {message.specialist}
              </div>
            )}
            {message.sources && (
              <div className='sources'>
                <span className='sources-label'>📚 Sources:</span>
                {message.sources.map((source, idx) => (
                  <span key={idx} className='source-tag'>
                    {source}
                  </span>
                ))}
              </div>
            )}
          </div>
        ))}

        {isTyping && (
          <div className='typing-indicator'>
            <span className='sender'>🎓 Chuck Missler AI</span>
            <div className='typing-dots'>
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        )}
      </div>

      <div className='input-area'>
        <textarea
          value={newMessage}
          onChange={(e) => setNewMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder='Ask Chuck Missler about Bible study, prophecy, theology...'
          className='chat-input'
          rows={3}
        />
        <button
          onClick={handleSendMessage}
          className='send-button'
          disabled={!newMessage.trim() || isTyping}
        >
          Send
        </button>
      </div>
    </div>
  );
};

export default ChatInterface;
