/** @format */

import React, { useState, useEffect } from "react";

interface Note {
  id: string;
  title: string;
  content: string;
  tags: string[];
  timestamp: Date;
  linkedVerses: string[];
  category: string;
}

// Add display mode types
type DisplayMode = "adaptive" | "compact" | "paginated";
type SortOption =
  | "newest"
  | "oldest"
  | "alphabetical"
  | "category"
  | "modified";

interface NoteStackProps {
  notes: Note[];
  activeNote: string | null;
  onNoteClick: (noteId: string) => void;
  isCompact?: boolean;
  isMinimized?: boolean;
}

const categories = [
  { id: "general", label: "General Study", icon: "📚" },
  { id: "prophecy", label: "Prophecy", icon: "🔮" },
  { id: "theology", label: "Theology", icon: "⛪" },
  { id: "apologetics", label: "Apologetics", icon: "🛡️" },
  { id: "personal", label: "Personal Insights", icon: "💭" },
];

const NoteStack: React.FC<NoteStackProps> = ({
  notes,
  activeNote,
  onNoteClick,
  isCompact = false,
  isMinimized = false,
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [isHoveredWhenMinimized, setIsHoveredWhenMinimized] = useState(false);
  const [hoverTimeout, setHoverTimeout] = useState<number | null>(null);

  // Add state for display controls
  const [currentPage, setCurrentPage] = useState(1);
  const [sortBy, setSortBy] = useState<SortOption>("newest");
  const [filterCategory, setFilterCategory] = useState<string>("");
  const [searchTerm, setSearchTerm] = useState("");

  // Determine display mode based on note count
  const getDisplayMode = (): DisplayMode => {
    if (notes.length <= 9) return "adaptive";
    if (notes.length <= 20) return "compact";
    return "paginated";
  };

  // Filter and sort notes
  const getFilteredAndSortedNotes = () => {
    let filtered = notes;

    // Apply category filter
    if (filterCategory) {
      filtered = filtered.filter((note) => note.category === filterCategory);
    }

    // Apply search filter
    if (searchTerm) {
      filtered = filtered.filter(
        (note) =>
          note.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
          note.content.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Apply sorting
    switch (sortBy) {
      case "newest":
        filtered = filtered.sort(
          (a, b) => b.timestamp.getTime() - a.timestamp.getTime()
        );
        break;
      case "oldest":
        filtered = filtered.sort(
          (a, b) => a.timestamp.getTime() - b.timestamp.getTime()
        );
        break;
      case "alphabetical":
        filtered = filtered.sort((a, b) => a.title.localeCompare(b.title));
        break;
      case "category":
        filtered = filtered.sort((a, b) =>
          a.category.localeCompare(b.category)
        );
        break;
      // Add more sorting options as needed
    }

    return filtered;
  };

  // Get notes for current page
  const getPaginatedNotes = () => {
    const filtered = getFilteredAndSortedNotes();
    const displayMode = getDisplayMode();

    if (displayMode === "paginated") {
      const notesPerPage = 20;
      const startIndex = (currentPage - 1) * notesPerPage;
      return filtered.slice(startIndex, startIndex + notesPerPage);
    }

    return filtered;
  };

  // Handle click outside to collapse
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (isExpanded) {
        const target = event.target as HTMLElement;
        if (!target.closest(".note-stack")) {
          setIsExpanded(false);
        }
      }
    };

    document.addEventListener("click", handleClickOutside);
    return () => document.removeEventListener("click", handleClickOutside);
  }, [isExpanded]);

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (hoverTimeout) {
        clearTimeout(hoverTimeout);
      }
    };
  }, [hoverTimeout]);

  // When minimized, collapse the stack and reset hover state
  useEffect(() => {
    if (isMinimized) {
      setIsExpanded(false);
      setIsHoveredWhenMinimized(false);
    }
  }, [isMinimized]);

  if (notes.length === 0) return null;

  const handleMouseEnter = () => {
    // Only handle hover when minimized AND NoteTaking component is open
    if (isMinimized) {
      // Clear any existing timeout
      if (hoverTimeout) {
        clearTimeout(hoverTimeout);
        setHoverTimeout(null);
      }
      setIsHoveredWhenMinimized(true);
    }
  };

  const handleMouseLeave = () => {
    // Only handle hover when minimized AND NoteTaking component is open
    if (isMinimized) {
      // Add delay before hiding to prevent jittering
      const timeout = setTimeout(() => {
        setIsHoveredWhenMinimized(false);
      }, 150);
      setHoverTimeout(timeout);
    }
  };

  const handleExpandClick = (e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent event bubbling
    e.preventDefault(); // Prevent default behavior

    console.log(
      "Button clicked - isMinimized:",
      isMinimized,
      "isExpanded:",
      isExpanded,
      "isHoveredWhenMinimized:",
      isHoveredWhenMinimized
    );

    // Clear any hover timeout when explicitly expanding
    if (hoverTimeout) {
      clearTimeout(hoverTimeout);
      setHoverTimeout(null);
    }

    // Always handle stack/unstack when the button is visible
    // The button only appears when either:
    // 1. Not minimized (normal operation)
    // 2. Minimized and hovered (after expanding from minimized state)

    if (isMinimized && isHoveredWhenMinimized) {
      // When minimized and hovered, treat it like normal stack/unstack
      // but also handle the hover state
      console.log(
        "Minimized hovered - toggling expanded from",
        isExpanded,
        "to",
        !isExpanded
      );
      setIsExpanded(!isExpanded);
    } else if (!isMinimized) {
      // When not minimized, normal stack/unstack behavior
      console.log(
        "Not minimized - toggling expanded from",
        isExpanded,
        "to",
        !isExpanded
      );
      setIsExpanded(!isExpanded);
    }
    // Note: We don't handle the case where isMinimized && !isHoveredWhenMinimized
    // because the button isn't visible in that state
  };

  const handleCardClick = (noteId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (isExpanded) {
      onNoteClick(noteId);
    }
  };

  // Calculate grid positions for expanded state
  const getGridPosition = (index: number) => {
    const displayMode = getDisplayMode();
    const cardsPerRow = displayMode === "adaptive" ? 3 : 4;
    const row = Math.floor(index / cardsPerRow);
    const col = index % cardsPerRow;

    // Adjust positioning based on display mode
    const cardSpacing = displayMode === "adaptive" ? 200 : 150;
    const verticalSpacing = displayMode === "adaptive" ? 140 : 90;

    return {
      x: col * cardSpacing - ((cardsPerRow - 1) * cardSpacing) / 2, // Center the grid
      y: -(row * verticalSpacing + 50), // Stack upward
    };
  };

  // Render controls header for compact and paginated modes
  const renderControlsHeader = () => {
    const displayMode = getDisplayMode();
    if (displayMode === "adaptive") return null;

    const totalFiltered = getFilteredAndSortedNotes().length;
    const totalPages = Math.ceil(totalFiltered / 20);

    return (
      <div className='note-stack-controls'>
        <div className='controls-row'>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as SortOption)}
            className='sort-select'
          >
            <option value='newest'>Newest First</option>
            <option value='oldest'>Oldest First</option>
            <option value='alphabetical'>A-Z</option>
            <option value='category'>Category</option>
          </select>

          <select
            value={filterCategory}
            onChange={(e) => setFilterCategory(e.target.value)}
            className='filter-select'
          >
            <option value=''>All Categories</option>
            {categories.map((cat) => (
              <option key={cat.id} value={cat.id}>
                {cat.label}
              </option>
            ))}
          </select>

          <input
            type='text'
            placeholder='Search notes...'
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className='search-input'
          />
        </div>

        {displayMode === "paginated" && totalPages > 1 && (
          <div className='pagination-controls'>
            <button
              onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
              disabled={currentPage === 1}
            >
              ‹
            </button>
            <span>
              {currentPage} of {totalPages}
            </span>
            <button
              onClick={() =>
                setCurrentPage(Math.min(totalPages, currentPage + 1))
              }
              disabled={currentPage === totalPages}
            >
              ›
            </button>
          </div>
        )}
      </div>
    );
  };

  const displayedNotes = getPaginatedNotes();

  return (
    <div
      className={`note-stack ${isCompact ? "compact" : ""} ${
        isExpanded ? "expanded" : ""
      } ${isMinimized ? "minimized" : ""} ${
        isMinimized && isHoveredWhenMinimized ? "hovered-minimized" : ""
      } ${getDisplayMode()}`}
      onMouseEnter={isMinimized ? handleMouseEnter : undefined}
      onMouseLeave={isMinimized ? handleMouseLeave : undefined}
    >
      {/* Controls Header - Show when expanded and not minimized */}
      {isExpanded && !isMinimized && renderControlsHeader()}

      {/* Expand/Collapse Button - Always show when not minimized, or when minimized and hovered */}
      {!isMinimized || (isMinimized && isHoveredWhenMinimized) ? (
        <button
          className={`note-stack-button ${isExpanded ? "expanded" : ""}`}
          onClick={handleExpandClick}
          title={
            isMinimized && isHoveredWhenMinimized
              ? "Restack notes"
              : isExpanded
              ? "Stack notes"
              : "Unstack notes"
          }
        >
          {isMinimized && isHoveredWhenMinimized
            ? "📝 ▼"
            : isExpanded
            ? "📝 ▼"
            : "📝 ▲"}
        </button>
      ) : null}

      {/* Minimized indicator - Only show when minimized and NOT hovered */}
      {isMinimized && !isHoveredWhenMinimized && (
        <div
          className='minimized-indicator'
          onClick={() => setIsHoveredWhenMinimized(true)}
        >
          📝 {notes.length}
        </div>
      )}

      {/* Note Cards */}
      {displayedNotes.map((note, index) => {
        const gridPos = getGridPosition(index);
        return (
          <div
            key={note.id}
            className={`note-card ${activeNote === note.id ? "active" : ""} ${
              isCompact ? "compact-card" : ""
            } ${getDisplayMode()}`}
            style={{
              zIndex: notes.length - index,
              transform: isExpanded
                ? `translateX(${gridPos.x}px) translateY(${gridPos.y}px) rotate(0deg)`
                : `translateX(${index * 3}px) translateY(${
                    index * -6
                  }px) rotate(${(index % 2 === 0 ? 1 : -1) * (index * 2)}deg)`,
              transitionDelay: isExpanded
                ? `${index * 80}ms`
                : `${(notes.length - index) * 40}ms`,
            }}
            onClick={(e) => handleCardClick(note.id, e)}
          >
            <div className='note-card-header'>
              <span className='note-icon'>
                {categories.find((cat) => cat.id === note.category)?.icon}
              </span>
              <h4 className='note-card-title'>{note.title}</h4>
            </div>
            <div className='note-card-content'>
              {note.content.substring(0, isCompact ? 40 : 80)}...
            </div>
            <div className='note-card-footer'>
              <span className='note-date'>
                {note.timestamp.toLocaleDateString()}
              </span>
              <div className='note-tags-preview'>
                {note.tags.slice(0, 2).map((tag) => (
                  <span key={tag} className='tag-mini'>
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default NoteStack;
