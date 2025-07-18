/** @format */

import { motion } from "framer-motion";
import "./UserProfileModal.css";

interface UserProfileModalProps {
  onClose: () => void;
  setShowChatHistory: (show: boolean) => void;
  showChatHistory: boolean;
}

const UserProfileModal = ({
  onClose,
  setShowChatHistory,
  showChatHistory,
}: UserProfileModalProps) => {
  return (
    <motion.div
      className='modal-backdrop'
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      onClick={onClose}
    >
      <motion.div
        className='modal-content'
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        transition={{ type: "spring", stiffness: 300, damping: 30 }}
        onClick={(e: React.MouseEvent) => e.stopPropagation()} // Prevent closing when clicking inside
      >
        <div className='modal-header'>
          <h2>User Controls</h2>
          <button className='close-modal-button' onClick={onClose}>
            ×
          </button>
        </div>
        <div className='modal-body'>
          <button
            className='modal-button'
            onClick={() => {
              setShowChatHistory(!showChatHistory);
              onClose();
            }}
          >
            {showChatHistory ? "💬 Hide History" : "💬 Show History"}
          </button>
          <button className='modal-button'>⚙️ Settings</button>
        </div>
      </motion.div>
    </motion.div>
  );
};

export default UserProfileModal;
