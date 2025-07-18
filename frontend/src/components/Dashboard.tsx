/** @format */

import React, { useState, useRef, useEffect } from "react";

interface Agent {
  id: string;
  name: string;
  role: string;
  avatar: string;
  greeting: string;
  responses: string[];
}

interface ChatMessage {
  id: string;
  content: string;
  isUser: boolean;
  avatar: string;
  timestamp: Date;
}

const Dashboard: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [currentAgent, setCurrentAgent] = useState<Agent>({
    id: "chuck",
    name: "Chuck Missler",
    role: "Master Biblical Teacher",
    avatar: "👨‍🏫",
    greeting:
      "Welcome to our study of God's amazing Word! I'm here to help you discover the incredible design and supernatural nature of Scripture. What would you like to explore today?",
    responses: [
      "The Bible is truly an extraterrestrial message from outside our time domain. What specific aspect would you like to explore?",
      "Remember, every detail in Scripture is there by deliberate design. God's precision is mathematically astounding!",
      "The integration of science and faith reveals God's magnificent handiwork. Let's dive deeper into His Word together.",
      "As we study together, keep in mind that Scripture interprets Scripture. The Bible is its own commentary.",
    ],
  });
  const [selectedAgentId, setSelectedAgentId] = useState("chuck");
  const chatContainerRef = useRef<HTMLDivElement>(null);

  const agents: Agent[] = [
    {
      id: "scholar",
      name: "Dr. Sarah",
      role: "Biblical Scholar",
      avatar: "📚",
      greeting:
        "I'm here to help you understand the deeper meanings and cross-references within Scripture.",
      responses: [
        "The original Hebrew and Greek texts reveal incredible depth that's sometimes lost in translation.",
        "Cross-referencing this passage with other scriptures shows a beautiful pattern of God's consistency.",
        "The historical context of this passage adds significant meaning to our understanding.",
        "Let me show you how this connects to the overall narrative of redemption throughout Scripture.",
      ],
    },
    {
      id: "crypto",
      name: "Prof. David",
      role: "Cryptographer",
      avatar: "🔢",
      greeting:
        "I specialize in discovering the hidden mathematical patterns and codes within Scripture.",
      responses: [
        "The mathematical precision in this passage is extraordinary - far beyond human possibility.",
        "When we analyze the letter patterns, we find deliberate design that spans multiple books.",
        "The statistical probability of these patterns occurring by chance is essentially zero.",
        "These numerical relationships demonstrate the supernatural origin of Scripture.",
      ],
    },
    {
      id: "prophecy",
      name: "Dr. Michael",
      role: "Prophecy Expert",
      avatar: "🔮",
      greeting:
        "I focus on prophetic studies and the mathematical precision of fulfilled prophecy.",
      responses: [
        "The prophetic timeline here is mathematically precise to the very day!",
        "This prophecy demonstrates God's sovereignty over time and history.",
        "The probability calculations show this could only be accomplished by divine intervention.",
        "We're seeing the unfolding of God's eternal plan with perfect timing.",
      ],
    },
    {
      id: "archaeology",
      name: "Dr. Rachel",
      role: "Archaeologist",
      avatar: "🏺",
      greeting:
        "I provide archaeological and historical validation of biblical accounts.",
      responses: [
        "Recent archaeological discoveries continue to confirm the historical accuracy of Scripture.",
        "The cultural context of this passage illuminates its deeper meaning.",
        "Historical records from this period perfectly align with the biblical account.",
        "Archaeological evidence provides powerful confirmation of Scripture's reliability.",
      ],
    },
  ];

  // Initialize with greeting message
  useEffect(() => {
    const initialMessage: ChatMessage = {
      id: "1",
      content: currentAgent.greeting,
      isUser: false,
      avatar: currentAgent.avatar,
      timestamp: new Date(),
    };
    setMessages([initialMessage]);
  }, [currentAgent.greeting, currentAgent.avatar]);

  // Auto-scroll to bottom when new messages are added
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop =
        chatContainerRef.current.scrollHeight;
    }
  }, [messages]);

  const generateResponse = (userMessage: string): string => {
    const lowerMessage = userMessage.toLowerCase();

    if (lowerMessage.includes("prophecy") || lowerMessage.includes("future")) {
      return (
        currentAgent.responses[0] ||
        "That's a fascinating prophetic insight! The mathematical precision of fulfilled prophecy is truly remarkable."
      );
    } else if (
      lowerMessage.includes("design") ||
      lowerMessage.includes("pattern")
    ) {
      return (
        currentAgent.responses[1] ||
        "The deliberate design in Scripture is mathematically impossible to occur by chance."
      );
    } else if (
      lowerMessage.includes("science") ||
      lowerMessage.includes("evidence")
    ) {
      return (
        currentAgent.responses[2] ||
        "The integration of scientific discovery with biblical truth continues to amaze me."
      );
    } else {
      return currentAgent.responses[
        Math.floor(Math.random() * currentAgent.responses.length)
      ];
    }
  };

  const sendMessage = () => {
    if (!inputValue.trim()) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      content: inputValue,
      isUser: true,
      avatar: "👤",
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");

    // Simulate AI response
    setTimeout(() => {
      const response = generateResponse(inputValue);
      const agentMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        content: response,
        isUser: false,
        avatar: currentAgent.avatar,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, agentMessage]);
    }, 1000);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      sendMessage();
    }
  };

  const selectAgent = (agentId: string) => {
    const agent = agents.find((a) => a.id === agentId);
    if (agent) {
      setCurrentAgent(agent);
      setSelectedAgentId(agentId);

      // Add greeting message from new agent
      const greetingMessage: ChatMessage = {
        id: Date.now().toString(),
        content: agent.greeting,
        isUser: false,
        avatar: agent.avatar,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, greetingMessage]);
    }
  };

  return (
    <section id='dashboard' className='section active'>
      <div className='container'>
        <h2>Your Biblical Study Dashboard</h2>
        <div className='dashboard-grid'>
          <div className='card'>
            <div className='card__header'>
              <h3>Chuck Missler AI Assistant</h3>
              <div className='status status--success'>Online</div>
            </div>
            <div className='card__body'>
              <div className='agent-chat' ref={chatContainerRef}>
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`chat-message ${
                      message.isUser ? "user-message" : "agent-message"
                    }`}
                  >
                    <div className='message-avatar'>{message.avatar}</div>
                    <div className='message-content'>
                      <p>{message.content}</p>
                    </div>
                  </div>
                ))}
                <div className='chat-input'>
                  <input
                    type='text'
                    className='form-control'
                    placeholder='Ask Chuck about any biblical topic...'
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyPress={handleKeyPress}
                  />
                  <button className='btn btn--primary' onClick={sendMessage}>
                    Send
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div className='card'>
            <div className='card__header'>
              <h3>Recent Study Progress</h3>
            </div>
            <div className='card__body'>
              <div className='progress-item'>
                <div className='progress-info'>
                  <h4>Daniel's 70 Weeks</h4>
                  <p>Prophetic timeline analysis</p>
                </div>
                <div className='progress-bar'>
                  <div className='progress-fill' style={{ width: "75%" }}></div>
                </div>
              </div>
              <div className='progress-item'>
                <div className='progress-info'>
                  <h4>Revelation Study</h4>
                  <p>End times prophecy</p>
                </div>
                <div className='progress-bar'>
                  <div className='progress-fill' style={{ width: "45%" }}></div>
                </div>
              </div>
              <div className='progress-item'>
                <div className='progress-info'>
                  <h4>Genesis Patterns</h4>
                  <p>Hidden design elements</p>
                </div>
                <div className='progress-bar'>
                  <div className='progress-fill' style={{ width: "90%" }}></div>
                </div>
              </div>
            </div>
          </div>

          <div className='card'>
            <div className='card__header'>
              <h3>Available Agents</h3>
            </div>
            <div className='card__body'>
              <div className='agent-grid'>
                {agents.map((agent) => (
                  <div
                    key={agent.id}
                    className={`agent-card ${
                      selectedAgentId === agent.id ? "active" : ""
                    }`}
                    onClick={() => selectAgent(agent.id)}
                  >
                    <div className='agent-avatar'>{agent.avatar}</div>
                    <h4>{agent.name}</h4>
                    <p>{agent.role}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Dashboard;
