/** @format */

import React from "react";

interface WelcomeProps {
  setActiveSection: (section: string) => void;
}

const Welcome: React.FC<WelcomeProps> = ({ setActiveSection }) => {
  return (
    <section id='welcome' className='section active'>
      <div className='container'>
        <div className='welcome-hero'>
          <div className='hero-content'>
            <div className='hero-image'>
              <div className='portrait-placeholder'>
                <div className='portrait-icon'>👨‍🏫</div>
              </div>
            </div>
            <div className='hero-text'>
              <h1>Welcome to God's Amazing Word</h1>
              <blockquote className='hero-quote'>
                "The Bible is a message system - it's not simply 66 books penned
                by 40 authors over 2,000 years. It's an integrated message
                system."
              </blockquote>
              <p className='hero-description'>
                Join us in discovering the incredible design and supernatural
                nature of Scripture through cutting-edge AI technology and
                rigorous biblical scholarship.
              </p>
              <button
                className='btn btn--primary btn--lg'
                onClick={() => setActiveSection("dashboard")}
              >
                Begin Your Study
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Welcome;
