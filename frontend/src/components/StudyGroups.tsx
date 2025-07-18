/** @format */

import React, { useState } from "react";

interface StudyGroup {
  id: string;
  name: string;
  members: number;
  topic: string;
  lastActive: string;
  messages: Message[];
}

interface Message {
  id: string;
  user: string;
  content: string;
  timestamp: string;
  type: "text" | "verse" | "insight";
}

const StudyGroups: React.FC = () => {
  const [activeGroup, setActiveGroup] = useState<string>("end-times");
  const [newMessage, setNewMessage] = useState<string>("");
  const [messageType, setMessageType] = useState<"text" | "verse" | "insight">(
    "text"
  );
  const [currentUser] = useState<string>("You");

  const [studyGroups, setStudyGroups] = useState<StudyGroup[]>([
    {
      id: "end-times",
      name: "End Times Study",
      members: 24,
      topic: "Prophetic Timeline",
      lastActive: "2 min ago",
      messages: [
        {
          id: "1",
          user: "Pastor Mike",
          content:
            "The prophecy of Daniel 9:24-27 provides a clear timeline for the end times. What are your thoughts on the 'one week' mentioned?",
          timestamp: "10:30 AM",
          type: "text",
        },
        {
          id: "2",
          user: "Sarah J.",
          content:
            "Daniel 9:27 - 'And he shall confirm the covenant with many for one week'",
          timestamp: "10:35 AM",
          type: "verse",
        },
        {
          id: "3",
          user: "John D.",
          content:
            "I believe this refers to the final 7-year period before Christ's return. The 'he' refers to the Antichrist.",
          timestamp: "10:40 AM",
          type: "insight",
        },
      ],
    },
    {
      id: "genesis",
      name: "Genesis Deep Dive",
      members: 18,
      topic: "Creation Account",
      lastActive: "15 min ago",
      messages: [
        {
          id: "1",
          user: "Dr. Smith",
          content:
            "Let's examine the Hebrew word 'bara' in Genesis 1:1. This word implies creation ex nihilo - out of nothing.",
          timestamp: "9:45 AM",
          type: "text",
        },
        {
          id: "2",
          user: "Mary K.",
          content:
            "Genesis 1:1 - 'In the beginning God created the heavens and the earth.'",
          timestamp: "9:50 AM",
          type: "verse",
        },
      ],
    },
    {
      id: "prophecy",
      name: "Prophecy Patterns",
      members: 31,
      topic: "Biblical Patterns",
      lastActive: "1 hour ago",
      messages: [
        {
          id: "1",
          user: "Chuck M.",
          content:
            "Remember, prophecy often has multiple fulfillments. The principle of 'double reference' is key to understanding prophetic literature.",
          timestamp: "8:20 AM",
          type: "insight",
        },
      ],
    },
  ]);

  // Group selection is handled directly in onClick

  const handleSendMessage = () => {
    if (newMessage.trim()) {
      const newMsg: Message = {
        id: Date.now().toString(),
        user: currentUser,
        content: newMessage,
        timestamp: new Date().toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        }),
        type: messageType,
      };

      setStudyGroups((groups) =>
        groups.map((group) =>
          group.id === activeGroup
            ? {
                ...group,
                messages: [...group.messages, newMsg],
                lastActive: "now",
              }
            : group
        )
      );

      setNewMessage("");
      setMessageType("text");
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const getCurrentGroup = () => {
    return (
      studyGroups.find((group) => group.id === activeGroup) || studyGroups[0]
    );
  };

  const getMessageIcon = (type: string) => {
    switch (type) {
      case "verse":
        return "📖";
      case "insight":
        return "💡";
      default:
        return "💬";
    }
  };

  return (
    <section id='study-groups' className='section active'>
      <div className='container'>
        <h2>Collaborative Study Groups</h2>
        <div className='study-groups-layout'>
          <div className='groups-sidebar'>
            <div className='card'>
              <div className='card__header'>
                <h3>My Study Groups</h3>
              </div>
              <div className='card__body'>
                <div className='group-list'>
                  {studyGroups.map((group) => (
                    <div
                      key={group.id}
                      className={`group-item ${
                        activeGroup === group.id ? "active" : ""
                      }`}
                      onClick={() => setActiveGroup(group.id)}
                      style={{ cursor: "pointer" }}
                    >
                      <div className='group-icon'>
                        {group.id === "end-times"
                          ? "🔮"
                          : group.id === "genesis"
                          ? "📖"
                          : "🛡️"}
                      </div>
                      <div className='group-info'>
                        <h4>{group.name}</h4>
                        <p>
                          {group.members} members • {group.lastActive}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
                <button className='btn btn--primary btn--full-width mt-8'>
                  Create New Group
                </button>
              </div>
            </div>
          </div>

          <div className='groups-main'>
            <div className='card'>
              <div className='card__header'>
                <h3>Prophecy Study Group</h3>
                <div className='group-stats'>
                  <span className='status status--success'>12 members</span>
                </div>
              </div>
              <div className='card__body'>
                <div className='group-discussion'>
                  <div className='discussion-header'>
                    <h3>{getCurrentGroup().name}</h3>
                    <span className='topic-badge'>
                      {getCurrentGroup().topic}
                    </span>
                  </div>

                  <div className='messages-container'>
                    {getCurrentGroup().messages.map((message) => (
                      <div
                        key={message.id}
                        className={`message ${
                          message.user === currentUser ? "own-message" : ""
                        }`}
                      >
                        <div className='message-header'>
                          <span className='message-user'>{message.user}</span>
                          <span className='message-time'>
                            {message.timestamp}
                          </span>
                          <span className='message-type'>
                            {getMessageIcon(message.type)}
                          </span>
                        </div>
                        <div className='message-content'>{message.content}</div>
                      </div>
                    ))}
                  </div>

                  <div className='message-input'>
                    <div className='input-controls'>
                      <select
                        value={messageType}
                        onChange={(e) =>
                          setMessageType(
                            e.target.value as "text" | "verse" | "insight"
                          )
                        }
                        className='message-type-select'
                      >
                        <option value='text'>💬 Comment</option>
                        <option value='verse'>📖 Bible Verse</option>
                        <option value='insight'>💡 Insight</option>
                      </select>
                    </div>
                    <div className='input-area'>
                      <textarea
                        value={newMessage}
                        onChange={(e) => setNewMessage(e.target.value)}
                        onKeyPress={handleKeyPress}
                        placeholder='Share your thoughts, insights, or verses...'
                        className='message-textarea'
                        rows={3}
                      />
                      <button
                        onClick={handleSendMessage}
                        className='send-button'
                        disabled={!newMessage.trim()}
                      >
                        Send
                      </button>
                    </div>
                  </div>
                </div>

                <div className='group-sidebar'>
                  <div className='group-stats'>
                    <h4>Group Statistics</h4>
                    <div className='stat-item'>
                      <span className='stat-label'>Total Members:</span>
                      <span className='stat-value'>
                        {getCurrentGroup().members}
                      </span>
                    </div>
                    <div className='stat-item'>
                      <span className='stat-label'>Messages Today:</span>
                      <span className='stat-value'>
                        {getCurrentGroup().messages.length}
                      </span>
                    </div>
                    <div className='stat-item'>
                      <span className='stat-label'>Last Active:</span>
                      <span className='stat-value'>
                        {getCurrentGroup().lastActive}
                      </span>
                    </div>
                  </div>

                  <div className='study-resources'>
                    <h4>Study Resources</h4>
                    <div className='resource-links'>
                      <a href='#' className='resource-link'>
                        📚 Study Guide
                      </a>
                      <a href='#' className='resource-link'>
                        🎥 Video Teaching
                      </a>
                      <a href='#' className='resource-link'>
                        📝 Notes Template
                      </a>
                      <a href='#' className='resource-link'>
                        🔍 Cross References
                      </a>
                    </div>
                  </div>

                  <div className='prayer-requests'>
                    <h4>Prayer Requests</h4>
                    <div className='prayer-item'>
                      <span className='prayer-text'>
                        Wisdom in understanding prophecy
                      </span>
                      <span className='prayer-count'>🙏 12</span>
                    </div>
                    <div className='prayer-item'>
                      <span className='prayer-text'>
                        Unity in our discussions
                      </span>
                      <span className='prayer-count'>🙏 8</span>
                    </div>
                    <div className='prayer-item'>
                      <span className='prayer-text'>Spiritual growth</span>
                      <span className='prayer-count'>🙏 15</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default StudyGroups;
