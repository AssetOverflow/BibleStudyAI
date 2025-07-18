/** @format */

import React, { useState } from "react";

const BibleExplorer: React.FC = () => {
  const [selectedBook, setSelectedBook] = useState("genesis");
  const [chapter, setChapter] = useState(1);
  const [verse, setVerse] = useState(1);
  const [currentVerse, setCurrentVerse] = useState({
    reference: "Genesis 1:1",
    text: "In the beginning God created the heavens and the earth.",
    analysis:
      'This opening verse contains profound implications. The Hebrew word "Elohim" (God) is plural, hinting at the Trinity. The word "bara" (created) implies creation ex nihilo - from nothing. This verse establishes the foundation for all reality.',
  });
  const [crossRefs, setCrossRefs] = useState([
    {
      reference: "John 1:1",
      text: "In the beginning was the Word, and the Word was with God, and the Word was God.",
    },
    {
      reference: "Hebrews 11:3",
      text: "By faith we understand that the worlds were framed by the word of God...",
    },
    {
      reference: "Colossians 1:16",
      text: "For by him all things were created: things in heaven and on earth...",
    },
  ]);

  const analyzeVerse = () => {
    setCurrentVerse((prev) => ({
      ...prev,
      analysis:
        "This verse contains layers of meaning that reveal God's incredible design. The Hebrew word structure shows deliberate mathematical patterns that span across multiple books. The cross-references create a web of interconnected truth that could only be designed by an infinite intelligence. Notice how this connects to the overall redemptive theme throughout Scripture - every detail serves the greater narrative of God's love for mankind.",
    }));
  };

  const findCrossRefs = () => {
    setCrossRefs([
      {
        reference: "Colossians 1:16-17",
        text: "For by him all things were created... He is before all things, and in him all things hold together.",
      },
      {
        reference: "Hebrews 1:3",
        text: "...sustaining all things by his powerful word.",
      },
      {
        reference: "Psalm 33:6",
        text: "By the word of the LORD the heavens were made...",
      },
      {
        reference: "Isaiah 55:11",
        text: "So is my word that goes out from my mouth: It will not return to me empty...",
      },
    ]);
  };

  const showOriginalText = () => {
    setCurrentVerse((prev) => ({
      ...prev,
      text: "בְּרֵאשִׁית בָּרָא אֱלֹהִים אֵת הַשָּׁמַיִם וְאֵת הָאָרֶץ",
      analysis:
        "Hebrew: B'reshit bara Elohim et hashamayim v'et ha'aretz. Literal: In beginning created God the heavens and the earth. This Hebrew text contains incredible depth and precision that demonstrates divine authorship.",
    }));
  };

  const findPatterns = () => {
    setCurrentVerse((prev) => ({
      ...prev,
      analysis:
        "Analyzing the numerical patterns in this verse reveals extraordinary design! The Hebrew text contains 7 words and 28 letters (7x4). The first verse of the Bible establishes the mathematical foundation that runs throughout all of Scripture. This is just the beginning of God's incredible numeric signature!",
    }));
  };

  return (
    <section id='bible-explorer' className='section active'>
      <div className='container'>
        <h2>Interactive Bible Explorer</h2>
        <div className='explorer-layout'>
          <div className='explorer-sidebar'>
            <div className='card'>
              <div className='card__header'>
                <h3>Scripture Navigation</h3>
              </div>
              <div className='card__body'>
                <div className='form-group'>
                  <label className='form-label'>Book</label>
                  <select
                    className='form-control'
                    value={selectedBook}
                    onChange={(e) => setSelectedBook(e.target.value)}
                  >
                    <option value='genesis'>Genesis</option>
                    <option value='exodus'>Exodus</option>
                    <option value='daniel'>Daniel</option>
                    <option value='matthew'>Matthew</option>
                    <option value='revelation'>Revelation</option>
                  </select>
                </div>
                <div className='form-group'>
                  <label className='form-label'>Chapter</label>
                  <input
                    type='number'
                    className='form-control'
                    value={chapter}
                    onChange={(e) => setChapter(parseInt(e.target.value))}
                    min='1'
                    max='50'
                  />
                </div>
                <div className='form-group'>
                  <label className='form-label'>Verse</label>
                  <input
                    type='number'
                    className='form-control'
                    value={verse}
                    onChange={(e) => setVerse(parseInt(e.target.value))}
                    min='1'
                    max='50'
                  />
                </div>
              </div>
            </div>

            <div className='card'>
              <div className='card__header'>
                <h3>Study Tools</h3>
              </div>
              <div className='card__body'>
                <button
                  className='btn btn--secondary btn--full-width mb-8'
                  onClick={analyzeVerse}
                >
                  AI Analysis
                </button>
                <button
                  className='btn btn--secondary btn--full-width mb-8'
                  onClick={findCrossRefs}
                >
                  Cross References
                </button>
                <button
                  className='btn btn--secondary btn--full-width mb-8'
                  onClick={showOriginalText}
                >
                  Original Language
                </button>
                <button
                  className='btn btn--secondary btn--full-width'
                  onClick={findPatterns}
                >
                  Hidden Patterns
                </button>
              </div>
            </div>
          </div>

          <div className='explorer-main'>
            <div className='card'>
              <div className='card__header'>
                <h3>{currentVerse.reference}</h3>
              </div>
              <div className='card__body'>
                <div className='verse-text'>
                  <p className='scripture-verse'>{currentVerse.text}</p>
                </div>
                <div className='verse-analysis'>
                  <h4>Chuck's Insights:</h4>
                  <p>{currentVerse.analysis}</p>
                </div>
              </div>
            </div>

            <div className='card'>
              <div className='card__header'>
                <h3>Cross References</h3>
              </div>
              <div className='card__body'>
                <div className='cross-ref-grid'>
                  {crossRefs.map((ref, index) => (
                    <div key={index} className='cross-ref-item'>
                      <strong>{ref.reference}</strong>
                      <p>{ref.text}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default BibleExplorer;
