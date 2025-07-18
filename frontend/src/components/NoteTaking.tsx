/** @format */

import React, { useState } from "react";
import "./NoteTaking.css";

// Export the Note interface so it can be used in other components
export interface Note {
  id: string;
  title: string;
  content: string;
  tags: string[];
  timestamp: Date;
  linkedVerses: string[];
  category: string;
}

interface NoteTakingProps {
  onNotesChange?: (notes: Note[]) => void;
  onActiveNoteChange?: (activeNote: string | null) => void;
  activeNote?: string | null;
  searchTerm?: string;
  onSearchChange?: (searchTerm: string) => void;
}

const NoteTaking: React.FC<NoteTakingProps> = ({
  onNotesChange,
  onActiveNoteChange,
  activeNote: externalActiveNote,
  searchTerm: externalSearchTerm,
  onSearchChange,
}) => {
  const [notes, setNotes] = useState<Note[]>([
    {
      id: "1",
      title: "Daniel's 70 Weeks Prophecy",
      content:
        "The prophecy in Daniel 9:24-27 is one of the most precise prophecies in Scripture. Chuck Missler emphasized that this prophecy gives us the exact timeline for the Messiah's first coming...",
      tags: ["prophecy", "daniel", "messiah", "timeline"],
      timestamp: new Date(),
      linkedVerses: ["Daniel 9:24-27", "Matthew 24:15"],
      category: "prophecy",
    },
    {
      id: "2",
      title: "The Rapture Theory",
      content:
        "Chuck Missler's analysis of the pre-tribulation rapture, examining the Greek text and prophetic timeline...",
      tags: ["rapture", "prophecy", "eschatology"],
      timestamp: new Date(),
      linkedVerses: ["1 Thessalonians 4:16-17", "1 Corinthians 15:51-52"],
      category: "prophecy",
    },
    {
      id: "3",
      title: "Genesis Gap Theory",
      content:
        "Understanding the possible gap between Genesis 1:1 and 1:2, and its implications for creation theology...",
      tags: ["creation", "genesis", "theology"],
      timestamp: new Date(),
      linkedVerses: ["Genesis 1:1-2", "Isaiah 45:18"],
      category: "theology",
    },
  ]);
  const [activeNote, setActiveNote] = useState<string | null>(
    externalActiveNote || null
  );
  const [newNote, setNewNote] = useState({
    title: "",
    content: "",
    tags: [] as string[],
    category: "general",
  });
  const [searchTerm, setSearchTerm] = useState(externalSearchTerm || "");
  const [showNewNoteForm, setShowNewNoteForm] = useState(false);

  const categories = [
    { id: "general", label: "General Study", icon: "📚" },
    { id: "prophecy", label: "Prophecy", icon: "🔮" },
    { id: "theology", label: "Theology", icon: "⛪" },
    { id: "apologetics", label: "Apologetics", icon: "🛡️" },
    { id: "personal", label: "Personal Insights", icon: "💭" },
  ];

  // Handle search term changes
  const handleSearchChange = (term: string) => {
    setSearchTerm(term);
    if (onSearchChange) {
      onSearchChange(term);
    }
  };

  // Notify parent component of notes changes
  React.useEffect(() => {
    if (onNotesChange) {
      onNotesChange(notes);
    }
  }, [notes, onNotesChange]);

  // Notify parent component of active note changes
  React.useEffect(() => {
    if (onActiveNoteChange) {
      onActiveNoteChange(activeNote);
    }
  }, [activeNote, onActiveNoteChange]);

  // Handle external active note changes
  React.useEffect(() => {
    if (externalActiveNote !== undefined) {
      setActiveNote(externalActiveNote);
    }
  }, [externalActiveNote]);

  // Handle external search term changes
  React.useEffect(() => {
    if (externalSearchTerm !== undefined) {
      setSearchTerm(externalSearchTerm);
    }
  }, [externalSearchTerm]);

  const handleCreateNote = () => {
    if (newNote.title.trim() && newNote.content.trim()) {
      const note: Note = {
        id: Date.now().toString(),
        title: newNote.title,
        content: newNote.content,
        tags: newNote.tags,
        timestamp: new Date(),
        linkedVerses: [],
        category: newNote.category,
      };

      setNotes((prev) => [note, ...prev]);
      setNewNote({ title: "", content: "", tags: [], category: "general" });
      setShowNewNoteForm(false);
      setActiveNote(note.id);
    }
  };

  const handleDeleteNote = (noteId: string) => {
    setNotes((prev) => prev.filter((note) => note.id !== noteId));
    if (activeNote === noteId) {
      setActiveNote(null);
    }
  };

  const activeNoteData = notes.find((note) => note.id === activeNote);
  const isEditing = showNewNoteForm || activeNote;

  return (
    <div className={`note-taking ${isEditing ? "editing-mode" : ""}`}>
      {/* Compact Header - only shows when editing */}
      {isEditing && (
        <div className='compact-header'>
          <div className='compact-search'>
            <input
              type='text'
              placeholder='🔍 Search...'
              value={searchTerm}
              onChange={(e) => handleSearchChange(e.target.value)}
              className='compact-search-input'
            />
          </div>
          <button
            className='compact-new-btn'
            onClick={() => setShowNewNoteForm(true)}
            title='New Note'
          >
            ✍️
          </button>
        </div>
      )}

      {/* Full Action Bar - only shows when not editing */}
      {!isEditing && (
        <div className='quick-actions'>
          <button
            className='quick-action-btn new-note'
            onClick={() => setShowNewNoteForm(true)}
            title='New Note'
          >
            ✍️
          </button>
          <div className='search-container'>
            <input
              type='text'
              placeholder='🔍 Search notes...'
              value={searchTerm}
              onChange={(e) => handleSearchChange(e.target.value)}
              className='search-input'
            />
          </div>
          <button className='quick-action-btn filter' title='Filter Notes'>
            🏷️
          </button>
        </div>
      )}

      {/* Main Layout */}
      <div className='main-layout'>
        {/* Tools Sidebar - only visible when editing */}
        {isEditing && (
          <div className='tools-sidebar'>
            <div className='tool-group'>
              <h4>📝 Format</h4>
              <button className='tool-btn' title='Bold'>
                𝐁
              </button>
              <button className='tool-btn' title='Italic'>
                𝐼
              </button>
              <button className='tool-btn' title='Underline'>
                𝕌
              </button>
              <button className='tool-btn' title='List'>
                ≡
              </button>
            </div>
            <div className='tool-group'>
              <h4>📖 Bible</h4>
              <button className='tool-btn' title='Link Verse'>
                🔗
              </button>
              <button className='tool-btn' title='Open Bible'>
                📚
              </button>
              <button className='tool-btn' title='Search Bible'>
                🔍
              </button>
            </div>
            <div className='tool-group'>
              <h4>🏷️ Tags</h4>
              <button className='tool-btn' title='Add Tag'>
                +
              </button>
              <button className='tool-btn' title='Tag List'>
                #
              </button>
            </div>
            <div className='tool-group'>
              <h4>⚙️ Actions</h4>
              <button className='tool-btn' title='Save Note'>
                💾
              </button>
              <button className='tool-btn' title='Delete Note'>
                🗑️
              </button>
              <button className='tool-btn' title='Copy Link'>
                🔗
              </button>
            </div>
          </div>
        )}

        {/* Content Area */}
        <div className='note-workspace'>
          {showNewNoteForm ? (
            <div className='note-editor active-editor'>
              <div className='editor-header-minimal'>
                <select
                  value={newNote.category}
                  onChange={(e) =>
                    setNewNote({ ...newNote, category: e.target.value })
                  }
                  className='category-selector-minimal'
                >
                  {categories.map((cat) => (
                    <option key={cat.id} value={cat.id}>
                      {cat.icon} {cat.label}
                    </option>
                  ))}
                </select>
                <div className='editor-actions-minimal'>
                  <button
                    onClick={handleCreateNote}
                    className='save-btn-minimal'
                    title='Save Note'
                  >
                    💾
                  </button>
                  <button
                    onClick={() => setShowNewNoteForm(false)}
                    className='cancel-btn-minimal'
                    title='Cancel'
                  >
                    ❌
                  </button>
                </div>
              </div>
              <input
                type='text'
                placeholder='Note title...'
                value={newNote.title}
                onChange={(e) =>
                  setNewNote({ ...newNote, title: e.target.value })
                }
                className='title-input-full'
              />
              <textarea
                placeholder='Start writing your note...'
                value={newNote.content}
                onChange={(e) =>
                  setNewNote({ ...newNote, content: e.target.value })
                }
                className='content-input-full'
                rows={20}
              />
            </div>
          ) : activeNoteData ? (
            <div className='note-editor active-editor'>
              <div className='editor-header-minimal'>
                <div className='note-meta-info-minimal'>
                  <span className='category-badge-minimal'>
                    {
                      categories.find(
                        (cat) => cat.id === activeNoteData.category
                      )?.icon
                    }
                    {
                      categories.find(
                        (cat) => cat.id === activeNoteData.category
                      )?.label
                    }
                  </span>
                  <span className='date-info-minimal'>
                    {activeNoteData.timestamp.toLocaleDateString()}
                  </span>
                </div>
                <div className='editor-actions-minimal'>
                  <button className='action-btn-minimal edit'>✏️</button>
                  <button className='action-btn-minimal share'>🔗</button>
                  <button
                    className='action-btn-minimal delete'
                    onClick={() => handleDeleteNote(activeNoteData.id)}
                  >
                    🗑️
                  </button>
                </div>
              </div>
              <h2 className='note-title-display-full'>
                {activeNoteData.title}
              </h2>
              <div className='note-content-display-full'>
                <p>{activeNoteData.content}</p>
              </div>
              {activeNoteData.linkedVerses.length > 0 && (
                <div className='linked-verses-minimal'>
                  <h4>📖 Verses:</h4>
                  <div className='verse-links-minimal'>
                    {activeNoteData.linkedVerses.map((verse) => (
                      <span key={verse} className='verse-link-minimal'>
                        {verse}
                      </span>
                    ))}
                  </div>
                </div>
              )}
              {activeNoteData.tags.length > 0 && (
                <div className='note-tags-display-minimal'>
                  {activeNoteData.tags.map((tag) => (
                    <span key={tag} className='tag-chip-minimal'>
                      #{tag}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ) : (
            <div className='welcome-screen'>
              <div className='welcome-content'>
                <h3>📝 Your Biblical Notes</h3>
                <p>
                  Create a new note or select one from your collection below
                </p>
                <button
                  className='welcome-action'
                  onClick={() => setShowNewNoteForm(true)}
                >
                  ✍️ Start Writing
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default NoteTaking;
