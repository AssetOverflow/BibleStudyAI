/** @format */

import { motion } from "framer-motion";

const navItems = [
  { id: "bible-study", icon: "📖", label: "Bible Study" },
  { id: "research-lab", icon: "🔬", label: "Research Lab" },
  { id: "study-groups", icon: "👥", label: "Study Groups" },
];

interface VerticalNavProps {
  activeSection: string;
  setActiveSection: (section: string) => void;
}

const VerticalNav: React.FC<VerticalNavProps> = ({
  activeSection,
  setActiveSection,
}) => {
  return (
    <nav className='vertical-nav'>
      <ul>
        {navItems.map((item) => (
          <motion.li
            key={item.id}
            className={activeSection === item.id ? "active" : ""}
            onClick={() => setActiveSection(item.id)}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <div className='nav-item-content'>
              <span className='nav-icon'>{item.icon}</span>
              <span className='nav-label'>{item.label}</span>
            </div>
            {activeSection === item.id && (
              <motion.div
                className='active-indicator'
                layoutId='activeIndicator'
              />
            )}
          </motion.li>
        ))}
      </ul>
    </nav>
  );
};

export default VerticalNav;
