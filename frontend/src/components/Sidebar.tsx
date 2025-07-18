/** @format */

import React from "react";

interface SidebarProps {
  activeSection: string;
  setActiveSection: (section: string) => void;
}

const Sidebar: React.FC<SidebarProps> = ({
  activeSection,
  setActiveSection,
}) => {
  const menuItems = [
    { id: "bible-study", label: "Bible Study", icon: "📖" },
    { id: "research-lab", label: "Research Lab", icon: "🔬" },
    { id: "study-groups", label: "Study Groups", icon: "👥" },
  ];

  return (
    <aside className='sidebar'>
      <div className='sidebar-header'>
        <h2>Chuck Missler AI Ministry</h2>
      </div>
      <nav className='sidebar-nav'>
        <ul>
          {menuItems.map((item) => (
            <li key={item.id} className='nav-item'>
              <button
                onClick={() => setActiveSection(item.id)}
                className={`nav-link ${
                  activeSection === item.id ? "active" : ""
                }`}
              >
                <span className='nav-icon'>{item.icon}</span>
                <span className='nav-label'>{item.label}</span>
              </button>
            </li>
          ))}
        </ul>
      </nav>
    </aside>
  );
};

export default Sidebar;
