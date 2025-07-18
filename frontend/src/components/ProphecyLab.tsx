/** @format */

import React, { useEffect, useState } from "react";
import Chart from "chart.js/auto";

interface ProphecyData {
  total: number;
  fulfilled: number;
  accuracy: number;
  probability: string;
}

const ProphecyLab: React.FC = () => {
  const [prophecyType, setProphecyType] = useState("messianic");
  const [timePeriod, setTimePeriod] = useState("all");
  const [prophecyChart, setProphecyChart] = useState<Chart | null>(null);
  const [currentData, setCurrentData] = useState<ProphecyData>({
    total: 365,
    fulfilled: 365,
    accuracy: 100,
    probability: "1 in 10^125",
  });

  const prophecyData: { [key: string]: ProphecyData } = {
    messianic: {
      total: 365,
      fulfilled: 365,
      accuracy: 100,
      probability: "1 in 10^125",
    },
    daniel70: {
      total: 1,
      fulfilled: 1,
      accuracy: 100,
      probability: "1 in 10^6",
    },
    endtimes: {
      total: 1845,
      fulfilled: 1234,
      accuracy: 100,
      probability: "1 in 10^157",
    },
    israel: {
      total: 2534,
      fulfilled: 1956,
      accuracy: 100,
      probability: "1 in 10^89",
    },
  };

  // Chart initialization is now handled directly in useEffect

  // Chart update is now handled directly in useEffect

  const calculateProphecy = () => {
    const data = prophecyData[prophecyType] || prophecyData.messianic;
    setCurrentData(data);
  };

  useEffect(() => {
    const initChart = () => {
      const ctx = document.getElementById("prophecyChart") as HTMLCanvasElement;
      if (ctx) {
        const chart = new Chart(ctx, {
          type: "doughnut",
          data: {
            labels: ["Fulfilled", "Pending"],
            datasets: [
              {
                data: [
                  currentData.fulfilled,
                  currentData.total - currentData.fulfilled,
                ],
                backgroundColor: ["#21808D", "#FFC185"],
                borderWidth: 0,
              },
            ],
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                position: "bottom",
              },
            },
          },
        });
        setProphecyChart(chart);
      }
    };

    setTimeout(initChart, 100);
    return () => {
      if (prophecyChart) {
        prophecyChart.destroy();
      }
    };
  }, [currentData, prophecyChart]); // Include all dependencies

  useEffect(() => {
    if (prophecyChart) {
      prophecyChart.data.datasets[0].data = [
        currentData.fulfilled,
        currentData.total - currentData.fulfilled,
      ];
      prophecyChart.update();
    }
  }, [currentData, prophecyChart]);

  const getInsightText = () => {
    return `The mathematical analysis of these prophecies reveals probability rates that are essentially zero. With ${currentData.fulfilled.toLocaleString()} prophecies fulfilled with 100% accuracy, the chances of this occurring by human prediction alone are ${
      currentData.probability
    }. This demonstrates the supernatural origin and divine authorship of Scripture.`;
  };

  return (
    <section id='prophecy-lab' className='section active'>
      <div className='container'>
        <h2>Prophecy Analysis Laboratory</h2>
        <div className='prophecy-layout'>
          <div className='prophecy-tools'>
            <div className='card'>
              <div className='card__header'>
                <h3>Prophecy Calculator</h3>
              </div>
              <div className='card__body'>
                <div className='form-group'>
                  <label className='form-label'>Prophecy Type</label>
                  <select
                    className='form-control'
                    value={prophecyType}
                    onChange={(e) => setProphecyType(e.target.value)}
                  >
                    <option value='messianic'>Messianic Prophecies</option>
                    <option value='daniel70'>Daniel's 70 Weeks</option>
                    <option value='endtimes'>End Times</option>
                    <option value='israel'>Israel's Restoration</option>
                  </select>
                </div>
                <div className='form-group'>
                  <label className='form-label'>Time Period</label>
                  <select
                    className='form-control'
                    value={timePeriod}
                    onChange={(e) => setTimePeriod(e.target.value)}
                  >
                    <option value='all'>All Time</option>
                    <option value='ot'>Old Testament</option>
                    <option value='nt'>New Testament</option>
                    <option value='modern'>Modern Era</option>
                  </select>
                </div>
                <button
                  className='btn btn--primary btn--full-width'
                  onClick={calculateProphecy}
                >
                  Calculate Probability
                </button>
              </div>
            </div>

            <div className='card'>
              <div className='card__header'>
                <h3>Statistical Analysis</h3>
              </div>
              <div className='card__body'>
                <div className='stat-item'>
                  <div className='stat-label'>Total Prophecies</div>
                  <div className='stat-value'>
                    {currentData.total.toLocaleString()}
                  </div>
                </div>
                <div className='stat-item'>
                  <div className='stat-label'>Fulfilled</div>
                  <div className='stat-value'>
                    {currentData.fulfilled.toLocaleString()}
                  </div>
                </div>
                <div className='stat-item'>
                  <div className='stat-label'>Accuracy Rate</div>
                  <div className='stat-value'>{currentData.accuracy}%</div>
                </div>
                <div className='stat-item'>
                  <div className='stat-label'>Probability</div>
                  <div className='stat-value'>{currentData.probability}</div>
                </div>
              </div>
            </div>
          </div>

          <div className='prophecy-results'>
            <div className='card'>
              <div className='card__header'>
                <h3>Messianic Prophecy Analysis</h3>
              </div>
              <div className='card__body'>
                <div className='prophecy-chart'>
                  <canvas id='prophecyChart' width='400' height='200'></canvas>
                </div>
                <div className='prophecy-insights'>
                  <h4>Chuck's Analysis:</h4>
                  <p>{getInsightText()}</p>
                </div>
              </div>
            </div>

            <div className='card'>
              <div className='card__header'>
                <h3>Key Prophecies</h3>
              </div>
              <div className='card__body'>
                <div className='prophecy-list'>
                  <div className='prophecy-item'>
                    <div className='prophecy-ref'>Isaiah 53:5</div>
                    <div className='prophecy-text'>
                      But he was wounded for our transgressions...
                    </div>
                    <div className='prophecy-status'>✓ Fulfilled</div>
                  </div>
                  <div className='prophecy-item'>
                    <div className='prophecy-ref'>Micah 5:2</div>
                    <div className='prophecy-text'>
                      But you, Bethlehem Ephrathah...
                    </div>
                    <div className='prophecy-status'>✓ Fulfilled</div>
                  </div>
                  <div className='prophecy-item'>
                    <div className='prophecy-ref'>Daniel 9:24-26</div>
                    <div className='prophecy-text'>
                      Seventy weeks are determined...
                    </div>
                    <div className='prophecy-status'>✓ Fulfilled</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default ProphecyLab;
