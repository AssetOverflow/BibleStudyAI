/** @format */

import React, { useState, useRef, useEffect } from "react";
import { FaEllipsisV } from "react-icons/fa";
import "./ChatHistory.css";

interface ChatSession {
  id: string;
  title: string;
  timestamp: Date;
  messageCount: number;
  topics: string[];
  specialists: string[];
}

const ChatHistory: React.FC = () => {
  const [openMenuId, setOpenMenuId] = useState<string | null>(null);
  const menuRef = useRef<HTMLDivElement>(null);

  const chatSessions: ChatSession[] = [
    {
      id: "1",
      title: "Daniel's 70 Weeks Prophecy",
      timestamp: new Date(Date.now() - 86400000), // 1 day ago
      messageCount: 15,
      topics: ["prophecy", "daniel", "messiah", "timeline"],
      specialists: ["Prophecy Specialist", "Biblical Scholar"],
    },
    {
      id: "2",
      title: "Revelation 12 Symbolism",
      timestamp: new Date(Date.now() - 172800000), // 2 days ago
      messageCount: 23,
      topics: ["revelation", "symbolism", "israel", "church"],
      specialists: [
        "Prophecy Specialist",
        "Biblical Scholar",
        "Apologetics Expert",
      ],
    },
    {
      id: "3",
      title: "The Doctrine of the Trinity",
      timestamp: new Date(Date.now() - 259200000), // 3 days ago
      messageCount: 8,
      topics: ["trinity", "theology", "godhead"],
      specialists: ["Apologetics Expert", "Biblical Scholar"],
    },
    {
      id: "4",
      title: "Genesis and Modern Science",
      timestamp: new Date(Date.now() - 345600000), // 4 days ago
      messageCount: 31,
      topics: ["genesis", "creation", "science"],
      specialists: ["Apologetics Expert"],
    },
  ];

  const toggleMenu = (id: string) => {
    setOpenMenuId(openMenuId === id ? null : id);
  };

  const handleClickOutside = (event: MouseEvent) => {
    if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
      setOpenMenuId(null);
    }
  };

  useEffect(() => {
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  return (
    <div className='chat-history-list'>
      <div className='history-header'>
        <h3>Chat History</h3>
      </div>
      {chatSessions.map((session) => (
        <div key={session.id} className='history-item'>
          <span className='item-title'>{session.title}</span>
          <div className='item-actions'>
            <button onClick={() => toggleMenu(session.id)}>
              <FaEllipsisV />
            </button>
            {openMenuId === session.id && (
              <div className='action-menu' ref={menuRef}>
                <button className='action-menu-item'>View</button>
                <button className='action-menu-item'>Rename</button>
                <button className='action-menu-item'>Delete</button>
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};

export default ChatHistory;
