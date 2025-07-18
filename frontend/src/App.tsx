/** @format */

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import BibleExplorer from "./components/BibleExplorer";
import ProphecyLab from "./components/ProphecyLab";
import StudyGroups from "./components/StudyGroups";
import NoteTaking, { type Note } from "./components/NoteTaking";
import NoteStack from "./components/NoteStack";
import ChatHistory from "./components/ChatHistory";
import ChatInterface from "./components/ChatInterface";
import UserProfileModal from "./components/UserProfileModal";
import {
  FaUserCircle,
  FaWindowRestore,
  FaWindowMinimize,
  FaComments,
  FaTimes,
} from "react-icons/fa";
import "./App.css";

const sections = [
  { id: "bible-study", icon: "📖", label: "Bible Study" },
  { id: "research-lab", icon: "🔬", label: "Research Lab" },
  { id: "study-groups", icon: "👥", label: "Study Groups" },
];

function App() {
  const [activeSection, setActiveSection] = useState("bible-study");
  const [showNotes, setShowNotes] = useState(false);
  const [showChatHistory, setShowChatHistory] = useState(true);
  const [showProfileModal, setShowProfileModal] = useState(false);
  const [notesPanelWidth, setNotesPanelWidth] = useState(400);
  const [showChatInterface, setShowChatInterface] = useState(false);

  // Note management state
  const [notes, setNotes] = useState<Note[]>([]);
  const [activeNote, setActiveNote] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState("");

  useEffect(() => {
    if (showNotes) {
      setShowChatHistory(false);
    }
  }, [showNotes]);

  useEffect(() => {
    if (showChatInterface) {
      setShowChatHistory(false);
    }
  }, [showChatInterface]);

  const handleResize = (e: React.MouseEvent) => {
    const startX = e.clientX;
    const startWidth = notesPanelWidth;

    const handleMouseMove = (e: MouseEvent) => {
      const newWidth = startWidth + (startX - e.clientX);
      setNotesPanelWidth(Math.max(350, Math.min(800, newWidth)));
    };

    const handleMouseUp = () => {
      document.removeEventListener("mousemove", handleMouseMove);
      document.removeEventListener("mouseup", handleMouseUp);
    };

    document.addEventListener("mousemove", handleMouseMove);
    document.addEventListener("mouseup", handleMouseUp);
  };

  const renderMainContent = () => {
    switch (activeSection) {
      case "bible-study":
        return <BibleExplorer />;
      case "research-lab":
        return <ProphecyLab />;
      case "study-groups":
        return <StudyGroups />;
      default:
        return <BibleExplorer />;
    }
  };

  // Filter notes based on search term
  const filteredNotes = notes.filter(
    (note) =>
      note.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      note.content.toLowerCase().includes(searchTerm.toLowerCase()) ||
      note.tags.some((tag) =>
        tag.toLowerCase().includes(searchTerm.toLowerCase())
      )
  );

  // Debug logging
  console.log("App component notes:", notes);
  console.log("App component filteredNotes:", filteredNotes);

  const handleNoteClick = (noteId: string) => {
    setActiveNote(noteId);
    setShowNotes(true); // Open notes panel when a note is clicked
  };

  return (
    <div className='app'>
      <motion.div className='main-ui'>
        <header className='app-header'>
          <div className='app-title'>
            <h1>
              Chuck Missler's Koinonia House - Advanced Biblical AI Ministry
            </h1>
            <p>
              An Interactive Biblical Research Platform built on cutting edge AI
              agents
            </p>
          </div>
          <div className='header-controls'>
            <button
              className='control-button user-profile-button'
              onClick={() => setShowProfileModal(true)}
              data-tooltip='User Profile'
            >
              <FaUserCircle size={24} />
            </button>
          </div>
        </header>

        <nav className='main-tabs'>
          {sections.map((section) => (
            <button
              key={section.id}
              className={`tab-button ${
                activeSection === section.id ? "active" : ""
              }`}
              onClick={() => setActiveSection(section.id)}
            >
              <span className='tab-icon'>{section.icon}</span>
              <span className='tab-label'>{section.label}</span>
            </button>
          ))}
        </nav>

        <main className='app-layout'>
          <AnimatePresence>
            {showChatHistory ? (
              <motion.aside
                className='sidebar'
                initial={{ width: 0, opacity: 0 }}
                animate={{ width: 250, opacity: 1 }}
                exit={{ width: 0, opacity: 0 }}
                transition={{ duration: 0.3 }}
              >
                <button
                  className='sidebar-toggle'
                  onClick={() => setShowChatHistory(!showChatHistory)}
                  data-tooltip='Toggle Chat History'
                >
                  <FaWindowRestore size={20} />
                </button>
                <motion.div
                  className='chat-history-container'
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  transition={{ duration: 0.3 }}
                >
                  <ChatHistory />
                </motion.div>
              </motion.aside>
            ) : (
              <motion.button
                className='sidebar-toggle sidebar-toggle-collapsed'
                onClick={() => setShowChatHistory(true)}
                data-tooltip='Show Chat History'
                initial={{ width: 40, opacity: 0 }}
                animate={{ width: 40, opacity: 1 }}
                exit={{ width: 0, opacity: 0 }}
                transition={{ duration: 0.3 }}
              >
                <FaWindowRestore size={20} />
              </motion.button>
            )}
          </AnimatePresence>
          <AnimatePresence mode='wait'>
            <motion.div
              key={activeSection}
              className={`content-area ${showNotes ? "notes-open" : ""}`}
              style={{
                marginRight: showNotes ? `${notesPanelWidth + 50}px` : "0px",
                transition: "margin-right 0.3s ease",
              }}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.5 }}
            >
              {renderMainContent()}
            </motion.div>
          </AnimatePresence>
        </main>
      </motion.div>

      <AnimatePresence>
        {/* Side tab hidden when notes are open */}
        {!showNotes && (
          <motion.div
            className='notes-tab'
            initial={{ x: 40 }}
            animate={{ x: 0 }}
            exit={{ x: 40 }}
            transition={{ duration: 0.3 }}
          >
            <button
              className='notes-tab-button'
              onClick={() => setShowNotes(true)}
              data-tooltip='Open Notes'
            >
              📝
            </button>
          </motion.div>
        )}
        {showNotes && (
          <motion.div
            className='overlay-panel notes-panel'
            style={{ width: notesPanelWidth }}
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{ type: "spring", stiffness: 300, damping: 30 }}
          >
            <div className='resize-handle' onMouseDown={handleResize}></div>
            <NoteTaking
              onNotesChange={setNotes}
              onActiveNoteChange={setActiveNote}
              activeNote={activeNote}
              searchTerm={searchTerm}
              onSearchChange={setSearchTerm}
            />
            <button
              className='close-button'
              onClick={() => setShowNotes(false)}
              title='Minimize Notes'
            >
              <FaWindowMinimize size={20} />
            </button>
          </motion.div>
        )}
        {showProfileModal && (
          <UserProfileModal
            onClose={() => setShowProfileModal(false)}
            setShowChatHistory={setShowChatHistory}
            showChatHistory={showChatHistory}
          />
        )}
        {showChatInterface && (
          <motion.div
            className='floating-chat-panel'
            initial={{ x: "-100%", opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: "-100%", opacity: 0 }}
            transition={{ type: "spring", stiffness: 300, damping: 30 }}
          >
            <div className='floating-chat-header'>
              <div className='chat-header-info'>
                <FaComments size={20} />
                <span className='chat-header-title'>Chuck Missler AI</span>
                <span className='chat-status'>Online</span>
              </div>
              <div className='chat-header-actions'>
                <button
                  className='chat-minimize-btn'
                  onClick={() => setShowChatInterface(false)}
                  data-tooltip='Minimize Chat'
                >
                  <FaWindowMinimize size={16} />
                </button>
                <button
                  className='chat-close-btn'
                  onClick={() => setShowChatInterface(false)}
                  data-tooltip='Close Chat'
                >
                  <FaTimes size={16} />
                </button>
              </div>
            </div>
            <div className='floating-chat-content'>
              <ChatInterface />
            </div>
          </motion.div>
        )}
        {!showChatInterface && (
          <motion.div
            className='floating-chat-bubble'
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0, opacity: 0 }}
            transition={{ type: "spring", stiffness: 300, damping: 20 }}
            onClick={() => setShowChatInterface(true)}
          >
            <div className='chat-bubble-content'>
              <FaComments size={24} />
              <div className='chat-bubble-text'>
                <span className='chat-title'>Chuck Missler AI</span>
                <span className='chat-subtitle'>Ask me anything</span>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Note Stack - Always visible at bottom when notes exist */}
      <NoteStack
        notes={filteredNotes}
        activeNote={activeNote}
        onNoteClick={handleNoteClick}
        isCompact={showNotes}
        isMinimized={!showNotes}
      />
    </div>
  );
}

export default App;
