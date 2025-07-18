/** @format */

import React from "react";

interface NavbarProps {
  activeSection: string;
  setActiveSection: (section: string) => void;
}

const Navbar: React.FC<NavbarProps> = ({ activeSection, setActiveSection }) => {
  const navLinks = [
    { id: "welcome", title: "Home" },
    { id: "dashboard", title: "Dashboard" },
    { id: "bible-explorer", title: "Bible Explorer" },
    { id: "knowledge-graph", title: "Knowledge Graph" },
    { id: "prophecy-lab", title: "Prophecy Lab" },
    { id: "study-groups", title: "Study Groups" },
  ];

  return (
    <nav className='navbar'>
      <div className='container'>
        <div className='navbar-brand'>
          <h2>Chuck Missler AI Ministry</h2>
          <p className='navbar-subtitle'>Advanced Biblical Teaching System</p>
        </div>
        <div className='navbar-nav'>
          {navLinks.map((link) => (
            <button
              key={link.id}
              className={`nav-link ${
                activeSection === link.id ? "active" : ""
              }`}
              onClick={() => setActiveSection(link.id)}
            >
              {link.title}
            </button>
          ))}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
