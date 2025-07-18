/** @format */

import React, { useState } from "react";

interface GraphNode {
  id: string;
  label: string;
  position: React.CSSProperties;
}

const KnowledgeGraph: React.FC = () => {
  const [focusTopic, setFocusTopic] = useState("creation");
  const [relationshipDepth, setRelationshipDepth] = useState(3);
  const [graphNodes, setGraphNodes] = useState<GraphNode[]>([
    {
      id: "genesis",
      label: "Genesis",
      position: { top: "50px", left: "100px" },
    },
    {
      id: "trinity",
      label: "Trinity",
      position: { top: "100px", right: "50px" },
    },
    {
      id: "design",
      label: "Design",
      position: { bottom: "80px", left: "80px" },
    },
    {
      id: "purpose",
      label: "Purpose",
      position: { bottom: "50px", right: "100px" },
    },
  ]);

  const topicData = {
    creation: {
      label: "Creation",
      nodes: [
        {
          id: "genesis",
          label: "Genesis",
          position: { top: "50px", left: "100px" },
        },
        {
          id: "trinity",
          label: "Trinity",
          position: { top: "100px", right: "50px" },
        },
        {
          id: "design",
          label: "Design",
          position: { bottom: "80px", left: "80px" },
        },
        {
          id: "purpose",
          label: "Purpose",
          position: { bottom: "50px", right: "100px" },
        },
      ],
    },
    redemption: {
      label: "Redemption",
      nodes: [
        {
          id: "sacrifice",
          label: "Sacrifice",
          position: { top: "60px", left: "90px" },
        },
        {
          id: "grace",
          label: "Grace",
          position: { top: "90px", right: "60px" },
        },
        {
          id: "salvation",
          label: "Salvation",
          position: { bottom: "90px", left: "70px" },
        },
        {
          id: "forgiveness",
          label: "Forgiveness",
          position: { bottom: "60px", right: "90px" },
        },
      ],
    },
    prophecy: {
      label: "Prophecy",
      nodes: [
        {
          id: "daniel",
          label: "Daniel",
          position: { top: "40px", left: "110px" },
        },
        {
          id: "revelation",
          label: "Revelation",
          position: { top: "110px", right: "40px" },
        },
        {
          id: "messiah",
          label: "Messiah",
          position: { bottom: "70px", left: "90px" },
        },
        {
          id: "timeline",
          label: "Timeline",
          position: { bottom: "40px", right: "110px" },
        },
      ],
    },
    covenant: {
      label: "Covenant",
      nodes: [
        {
          id: "abraham",
          label: "Abraham",
          position: { top: "70px", left: "80px" },
        },
        {
          id: "moses",
          label: "Moses",
          position: { top: "80px", right: "70px" },
        },
        {
          id: "david",
          label: "David",
          position: { bottom: "100px", left: "60px" },
        },
        {
          id: "newcovenant",
          label: "New Covenant",
          position: { bottom: "70px", right: "80px" },
        },
      ],
    },
    messiah: {
      label: "Messiah",
      nodes: [
        {
          id: "prophecies",
          label: "Prophecies",
          position: { top: "55px", left: "95px" },
        },
        {
          id: "fulfillment",
          label: "Fulfillment",
          position: { top: "95px", right: "55px" },
        },
        {
          id: "kingship",
          label: "Kingship",
          position: { bottom: "85px", left: "75px" },
        },
        {
          id: "priesthood",
          label: "Priesthood",
          position: { bottom: "55px", right: "95px" },
        },
      ],
    },
  };

  const updateGraph = () => {
    const topicInfo = topicData[focusTopic as keyof typeof topicData];
    if (topicInfo) {
      setGraphNodes(topicInfo.nodes);
    }
  };

  const handleNodeClick = (nodeId: string) => {
    console.log(`Clicked node: ${nodeId}`);
    // Could implement node detail view or navigation here
  };

  return (
    <section id='knowledge-graph' className='section active'>
      <div className='container'>
        <h2>Biblical Knowledge Graph</h2>
        <div className='graph-layout'>
          <div className='graph-controls'>
            <div className='card'>
              <div className='card__header'>
                <h3>Graph Controls</h3>
              </div>
              <div className='card__body'>
                <div className='form-group'>
                  <label className='form-label'>Focus Topic</label>
                  <select
                    className='form-control'
                    value={focusTopic}
                    onChange={(e) => setFocusTopic(e.target.value)}
                  >
                    <option value='creation'>Creation</option>
                    <option value='redemption'>Redemption</option>
                    <option value='prophecy'>Prophecy</option>
                    <option value='covenant'>Covenant</option>
                    <option value='messiah'>Messiah</option>
                  </select>
                </div>
                <div className='form-group'>
                  <label className='form-label'>Relationship Depth</label>
                  <input
                    type='range'
                    className='form-control'
                    min='1'
                    max='5'
                    value={relationshipDepth}
                    onChange={(e) =>
                      setRelationshipDepth(parseInt(e.target.value))
                    }
                  />
                  <div
                    style={{
                      textAlign: "center",
                      marginTop: "8px",
                      fontSize: "12px",
                    }}
                  >
                    Depth: {relationshipDepth}
                  </div>
                </div>
                <button
                  className='btn btn--primary btn--full-width'
                  onClick={updateGraph}
                >
                  Update Graph
                </button>
              </div>
            </div>
          </div>
          <div className='graph-visualization'>
            <div className='card'>
              <div className='card__header'>
                <h3>Biblical Concept Relationships</h3>
              </div>
              <div className='card__body'>
                <div className='knowledge-graph'>
                  <div className='graph-node central'>
                    <div className='node-content'>
                      {topicData[focusTopic as keyof typeof topicData]?.label ||
                        "Creation"}
                    </div>
                  </div>
                  {graphNodes.map((node) => (
                    <div
                      key={node.id}
                      className='graph-node'
                      style={node.position}
                      onClick={() => handleNodeClick(node.id)}
                    >
                      <div className='node-content'>{node.label}</div>
                    </div>
                  ))}
                  <svg className='graph-connections'>
                    <line
                      x1='50%'
                      y1='50%'
                      x2='30%'
                      y2='40%'
                      stroke='var(--color-primary)'
                      strokeWidth='2'
                    />
                    <line
                      x1='50%'
                      y1='50%'
                      x2='70%'
                      y2='35%'
                      stroke='var(--color-primary)'
                      strokeWidth='2'
                    />
                    <line
                      x1='50%'
                      y1='50%'
                      x2='25%'
                      y2='75%'
                      stroke='var(--color-primary)'
                      strokeWidth='2'
                    />
                    <line
                      x1='50%'
                      y1='50%'
                      x2='75%'
                      y2='80%'
                      stroke='var(--color-primary)'
                      strokeWidth='2'
                    />
                  </svg>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default KnowledgeGraph;
