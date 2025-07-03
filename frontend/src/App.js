import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import "./App.css";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from "recharts";

function App() {
    const [formData, setFormData] = useState({
        "Dst Port": "",
        "Flow Duration": "",
        "Tot Fwd Pkts": "",
        "Tot Bwd Pkts": "",
        "Flow Byts/s": "",
        "Flow Pkts/s": "",
        "Pkt Len Max": "",
        "Pkt Len Mean": "",
        "Pkt Len Std": "",
        "SYN Flag Cnt": "",
        "ACK Flag Cnt": "",
        "FIN Flag Cnt": ""
    });

    const featureLabels = {
        "Dst Port": "Destination Port",
        "Flow Duration": "Flow Duration (ms)",
        "Tot Fwd Pkts": "Total Forward Packets",
        "Tot Bwd Pkts": "Total Backward Packets",
        "Flow Byts/s": "Flow Bytes per Second",
        "Flow Pkts/s": "Flow Packets per Second",
        "Pkt Len Max": "Packet Length Maximum",
        "Pkt Len Mean": "Packet Length Mean",
        "Pkt Len Std": "Packet Length Standard Deviation",
        "SYN Flag Cnt": "SYN Flag Count",
        "ACK Flag Cnt": "ACK Flag Count",
        "FIN Flag Cnt": "FIN Flag Count"
    };

    const [prediction, setPrediction] = useState("");
    const [reason, setReason] = useState("");
    const [randomResults, setRandomResults] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [isContinuous, setIsContinuous] = useState(false);
    const [timeSeriesData, setTimeSeriesData] = useState([]);
    const [errorMessage, setErrorMessage] = useState("");
    const [activeTab, setActiveTab] = useState("form");
    const [showTips, setShowTips] = useState(false);
    const [selectedResult, setSelectedResult] = useState(null);
    const intervalRef = useRef(null);

    const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

    // Random data generation ranges
    const randomRanges = {
        "Dst Port": { min: 1, max: 65535 },
        "Flow Duration": { min: 10, max: 10000 },
        "Tot Fwd Pkts": { min: 1, max: 100 },
        "Tot Bwd Pkts": { min: 1, max: 100 },
        "Flow Byts/s": { min: 100, max: 100000 },
        "Flow Pkts/s": { min: 1, max: 1000 },
        "Pkt Len Max": { min: 40, max: 1500 },
        "Pkt Len Mean": { min: 40, max: 800 },
        "Pkt Len Std": { min: 0, max: 400 },
        "SYN Flag Cnt": { min: 0, max: 10 },
        "ACK Flag Cnt": { min: 0, max: 20 },
        "FIN Flag Cnt": { min: 0, max: 10 }
    };

    // Clean up interval on component unmount
    useEffect(() => {
        return () => {
            if (intervalRef.current) {
                clearInterval(intervalRef.current);
            }
        };
    }, []);

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsLoading(true);
        try {
            console.log("📌 Sending request to API:", formData);

            const response = await axios.post("http://127.0.0.1:5000/predict", formData);

            console.log("📌 API Response:", response.data);

            if (response.data && response.data.prediction) {
                setPrediction(response.data.prediction);
                
                // Extract full reason with feature name mapping
                let reasonText = response.data.reason || "No explanation provided.";
                Object.keys(featureLabels).forEach((key) => {
                    reasonText = reasonText.replace(key, featureLabels[key]);
                });

                setReason(reasonText);
                setErrorMessage("");
            } else {
                setPrediction("Unexpected response format");
                setReason("");
            }
        } catch (error) {
            console.error("❌ API Error:", error);
            setPrediction("Error making prediction.");
            setReason("");
            setErrorMessage("Failed to connect to API. Make sure the Flask server is running.");
        } finally {
            setIsLoading(false);
        }
    };

    const generateRandomValue = (min, max) => {
        return Math.floor(Math.random() * (max - min + 1)) + min;
    };

    const generateRandomData = () => {
        const randomData = {};
        Object.keys(randomRanges).forEach(feature => {
            const { min, max } = randomRanges[feature];
            randomData[feature] = generateRandomValue(min, max);
        });
        return randomData;
    };

    const handleGenerateRandom = async () => {
        setIsLoading(true);
        const randomData = generateRandomData();
        setFormData(randomData);
        
        // Automatically submit prediction request with random data
        try {
            const response = await axios.post("http://127.0.0.1:5000/predict", randomData);
            
            if (response.data && response.data.prediction) {
                setPrediction(response.data.prediction);
                
                let reasonText = response.data.reason || "No explanation provided.";
                Object.keys(featureLabels).forEach((key) => {
                    reasonText = reasonText.replace(key, featureLabels[key]);
                });
                
                setReason(reasonText);
                setErrorMessage("");
            }
        } catch (error) {
            console.error("❌ Random prediction error:", error);
            setPrediction("Error making prediction.");
            setReason("");
            setErrorMessage("Failed to connect to API. Make sure the Flask server is running.");
        } finally {
            setIsLoading(false);
        }
    };

    const toggleContinuousPrediction = () => {
        if (isContinuous) {
            // Stop continuous prediction
            if (intervalRef.current) {
                clearInterval(intervalRef.current);
                intervalRef.current = null;
            }
            setIsContinuous(false);
        } else {
            // Start continuous prediction
            setIsContinuous(true);
            
            // Reset time series data
            setTimeSeriesData([]);
            
            // Make first prediction immediately
            makeContinuousPrediction();
            
            // Then set interval for subsequent predictions
            intervalRef.current = setInterval(makeContinuousPrediction, 5000);
        }
    };

    const makeContinuousPrediction = async () => {
        const randomData = generateRandomData();
        setFormData(randomData);
        
        try {
            const response = await axios.post("http://127.0.0.1:5000/predict", randomData);
            
            if (response.data && response.data.prediction) {
                setPrediction(response.data.prediction);
                
                // Extract and format reason text
                let reasonText = response.data.reason || "No explanation provided.";
                Object.keys(featureLabels).forEach((key) => {
                    reasonText = reasonText.replace(key, featureLabels[key]);
                });
                
                setReason(reasonText);
                setErrorMessage("");
                
                // Update time series data
                const timestamp = new Date().toLocaleTimeString();
                
                setTimeSeriesData(prevData => {
                    // Keep only the most recent 20 data points
                    const newData = [...prevData, {
                        time: timestamp,
                        data: randomData,
                        prediction: response.data.prediction,
                        confidence: response.data.confidence || 0,
                        reason: reasonText  // Store reason with each data point
                    }];
                    
                    if (newData.length > 20) {
                        return newData.slice(newData.length - 20);
                    }
                    return newData;
                });
                
                // Update random results summary
                const maliciousCount = timeSeriesData.filter(item => item.prediction === "Malicious").length;
                const normalCount = timeSeriesData.filter(item => item.prediction === "Normal").length;
                
                setRandomResults([
                    ...timeSeriesData.map((item, index) => ({
                        id: index + 1,
                        data: item.data,
                        prediction: item.prediction,
                        time: item.time,
                        reason: item.reason || ""
                    })),
                    { 
                        chartData: [
                            { name: "Malicious", value: maliciousCount },
                            { name: "Normal", value: normalCount }
                        ]
                    }
                ]);
            }
        } catch (error) {
            console.error("❌ Continuous prediction error:", error);
            setErrorMessage("Failed to connect to API. Make sure the Flask server is running.");
            
            // Stop continuous prediction if there's an error
            if (intervalRef.current) {
                clearInterval(intervalRef.current);
                intervalRef.current = null;
            }
            setIsContinuous(false);
        }
    };

    const generateMultipleRandomPredictions = async (count = 10) => {
        setIsLoading(true);
        const results = [];
        let maliciousCount = 0;
        let normalCount = 0;

        for (let i = 0; i < count; i++) {
            const randomData = generateRandomData();
            try {
                const response = await axios.post("http://127.0.0.1:5000/predict", randomData);
                if (response.data && response.data.prediction) {
                    // Extract and format reason text
                    let reasonText = response.data.reason || "No explanation provided.";
                    Object.keys(featureLabels).forEach((key) => {
                        reasonText = reasonText.replace(key, featureLabels[key]);
                    });
                    
                    const result = {
                        id: i + 1,
                        data: randomData,
                        prediction: response.data.prediction,
                        reason: reasonText
                    };
                    
                    if (response.data.prediction === "Malicious") {
                        maliciousCount++;
                    } else {
                        normalCount++;
                    }
                    
                    results.push(result);
                    console.log(result);
                }
            } catch (error) {
                console.error(`❌ Error in batch prediction ${i+1}:`, error);
                setErrorMessage("Failed to connect to API. Make sure the Flask server is running.");
            }
        }

        setRandomResults([
            ...results,
            { 
                chartData: [
                    { name: "Malicious", value: maliciousCount },
                    { name: "Normal", value: normalCount }
                ]
            }
        ]);
        setIsLoading(false);
    };

    const renderPredictionDescription = () => {
        if (!prediction) return null;
        
        if (prediction === "Malicious") {
            return (
                <div className="prediction-description malicious">
                    <h3>⚠️ Potential Threat Detected</h3>
                    <p>This network traffic pattern displays characteristics commonly associated with malicious activity.</p>
                </div>
            );
        } else {
            return (
                <div className="prediction-description normal">
                    <h3>✅ Normal Traffic Pattern</h3>
                    <p>This network traffic appears to be legitimate and follows expected patterns.</p>
                </div>
            );
        }
    };

    const showResultDetails = (result) => {
        setSelectedResult(result);
    };

    // Function to render the data values in a readable format
    const renderDataValues = (data) => {
        if (!data) return null;
        
        return (
            <div className="data-values-panel">
                <h3>Traffic Parameters</h3>
                <div className="data-values-grid">
                    {Object.keys(data).map((key) => (
                        <div key={key} className="data-value-item">
                            <span className="data-label">{featureLabels[key] || key}:</span>
                            <span className="data-value">{data[key]}</span>
                        </div>
                    ))}
                </div>
            </div>
        );
    };

    return (
        <div className="container">
            <div className="header">
                <h1>🛡️ Network Guardian</h1>
                <p className="tagline">Advanced Network Intrusion Detection System</p>
            </div>
            
            {errorMessage && (
                <div className="error-message">
                    <span className="error-icon">⚠️</span> {errorMessage}
                </div>
            )}
            
            <div className="tab-container">
                <div className="tabs">
                    <button 
                        className={`tab ${activeTab === "form" ? "active" : ""}`}
                        onClick={() => setActiveTab("form")}
                    >
                        Manual Input
                    </button>
                    <button 
                        className={`tab ${activeTab === "continuous" ? "active" : ""}`}
                        onClick={() => setActiveTab("continuous")}
                    >
                        Continuous Monitoring
                    </button>
                    <button 
                        className={`tab ${activeTab === "batch" ? "active" : ""}`}
                        onClick={() => setActiveTab("batch")}
                    >
                        Batch Analysis
                    </button>
                    <button 
                        className={`tab ${activeTab === "help" ? "active" : ""}`}
                        onClick={() => setActiveTab("help")}
                    >
                        Help
                    </button>
                </div>
                
                <div className="info-panel">
                    <button className="tips-button" onClick={() => setShowTips(!showTips)}>
                        {showTips ? "Hide Tips" : "Show Tips"}
                    </button>
                    {showTips && (
                        <div className="tips">
                            <ul>
                                <li><strong>Manual Input:</strong> Enter your network traffic parameters manually</li>
                                <li><strong>Continuous Monitoring:</strong> Watch real-time predictions with auto-generated data</li>
                                <li><strong>Batch Analysis:</strong> Run multiple predictions at once for trend analysis</li>
                                <li><strong>Generate Random Values:</strong> Quickly test with random network traffic patterns</li>
                            </ul>
                        </div>
                    )}
                </div>
                
                {activeTab === "form" && (
                    <div className="tab-content">
                        <div className="action-buttons">
                            <button 
                                onClick={handleGenerateRandom} 
                                disabled={isLoading}
                                className="random-button"
                            >
                                🎲 Generate Random Values
                            </button>
                        </div>
                        
                        <form onSubmit={handleSubmit}>
                            <div className="form-grid">
                                {Object.keys(formData).map((feature, index) => (
                                    <div key={index} className="input-group">
                                        <label>{featureLabels[feature]}</label>
                                        <input
                                            type="number"
                                            name={feature}
                                            value={formData[feature]}
                                            placeholder={featureLabels[feature]}
                                            onChange={handleChange}
                                            required
                                        />
                                    </div>
                                ))}
                            </div>
                            <button type="submit" disabled={isLoading} className="submit-button">
                                🔍 Analyze Traffic
                            </button>
                        </form>

                        {isLoading && (
                            <div className="loading">
                                <div className="loader"></div>
                                <p>Analyzing network traffic...</p>
                            </div>
                        )}

                        {prediction && (
                            <div className={`prediction-result ${prediction.toLowerCase()}`}>
                                <h2>Prediction: {prediction}</h2>
                                {renderPredictionDescription()}
                                {reason && (
                                    <div className="reason-container">
                                        <h3>Analysis Details:</h3>
                                        <p className="reason">{reason}</p>
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                )}
                
                {activeTab === "continuous" && (
                    <div className="tab-content">
                        <div className="action-buttons">
                            <button 
                                onClick={toggleContinuousPrediction} 
                                className={`continuous-button ${isContinuous ? "active" : ""}`}
                            >
                                {isContinuous ? "⏹️ Stop Monitoring" : "▶️ Start Continuous Monitoring (5s)"}
                            </button>
                        </div>
                        
                        {isContinuous && (
                            <div className="live-status">
                                <div className="pulse"></div>
                                <span>Live Monitoring Active</span>
                            </div>
                        )}
                        
                        {prediction && isContinuous && (
                            <div className="current-prediction-container">
                                <div className={`prediction-result ${prediction.toLowerCase()}`}>
                                    <h2>Latest Prediction: {prediction}</h2>
                                    {renderPredictionDescription()}
                                </div>
                                
                                {/* Display current traffic parameters */}
                                {renderDataValues(formData)}
                            </div>
                        )}

                        {timeSeriesData.length > 0 && (
                            <div className="time-series-section">
                                <h2>Monitoring Timeline</h2>
                                
                                <div className="chart-container">
                                    <ResponsiveContainer width="100%" height={300}>
                                        <LineChart data={timeSeriesData.map((item, index) => ({
                                            name: item.time,
                                            isMalicious: item.prediction === "Malicious" ? 1 : 0,
                                            index: index
                                        }))}>
                                            <CartesianGrid strokeDasharray="3 3" />
                                            <XAxis dataKey="index" label={{ value: 'Prediction Number', position: 'bottom' }} />
                                            <YAxis domain={[0, 1]} ticks={[0, 1]} label={{ value: 'Traffic Status', angle: -90, position: 'insideLeft' }} />
                                            <Tooltip formatter={(value) => (value === 1 ? "Malicious" : "Normal")} />
                                            <Legend />
                                            <Line type="stepAfter" dataKey="isMalicious" name="Traffic Status" stroke="#ff7300" strokeWidth={2} />
                                        </LineChart>
                                    </ResponsiveContainer>
                                </div>
                                
                                <div className="charts-row">
                                    <div className="chart-container half-width">
                                        <h3>Results Distribution</h3>
                                        <ResponsiveContainer width="100%" height={300}>
                                            <PieChart>
                                                <Pie
                                                    data={[
                                                        { name: "Malicious", value: timeSeriesData.filter(item => item.prediction === "Malicious").length },
                                                        { name: "Normal", value: timeSeriesData.filter(item => item.prediction === "Normal").length }
                                                    ]}
                                                    cx="50%"
                                                    cy="50%"
                                                    labelLine={false}
                                                    outerRadius={100}
                                                    fill="#8884d8"
                                                    dataKey="value"
                                                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                                                >
                                                    {[
                                                        { name: "Malicious", value: timeSeriesData.filter(item => item.prediction === "Malicious").length },
                                                        { name: "Normal", value: timeSeriesData.filter(item => item.prediction === "Normal").length }
                                                    ].map((entry, index) => (
                                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                                    ))}
                                                </Pie>
                                                <Tooltip formatter={(value) => [value, "Count"]} />
                                            </PieChart>
                                        </ResponsiveContainer>
                                    </div>
                                    
                                    <div className="chart-container half-width">
                                        <h3>Results Distribution</h3>
                                        <ResponsiveContainer width="100%" height={300}>
                                            <BarChart data={[
                                                { name: "Malicious", value: timeSeriesData.filter(item => item.prediction === "Malicious").length },
                                                { name: "Normal", value: timeSeriesData.filter(item => item.prediction === "Normal").length }
                                            ]}>
                                                <CartesianGrid strokeDasharray="3 3" />
                                                <XAxis dataKey="name" />
                                                <YAxis label={{ value: 'Count', angle: -90, position: 'insideLeft' }} />
                                                <Tooltip />
                                                <Legend />
                                                <Bar dataKey="value" name="Number of Predictions" fill="#8884d8">
                                                    {[
                                                        { name: "Malicious", value: timeSeriesData.filter(item => item.prediction === "Malicious").length },
                                                        { name: "Normal", value: timeSeriesData.filter(item => item.prediction === "Normal").length }
                                                    ].map((entry, index) => (
                                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                                    ))}
                                                </Bar>
                                            </BarChart>
                                        </ResponsiveContainer>
                                    </div>
                                </div>
                                
                                <h3>Recent Alert History</h3>
                                <div className="results-table">
                                    <table>
                                        <thead>
                                            <tr>
                                                <th>#</th>
                                                <th>Time</th>
                                                <th>Status</th>
                                                <th>Actions</th>
                                                <th>Reason</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {timeSeriesData.slice().reverse().map((result, index) => (
                                                <tr key={index} className={result.prediction.toLowerCase()}>
                                                    <td>{timeSeriesData.length - index}</td>
                                                    <td>{result.time}</td>
                                                    <td className="status-cell">
                                                        <span className={`status-icon ${result.prediction.toLowerCase()}`}>
                                                            {result.prediction === "Malicious" ? "⚠️" : "✅"}
                                                        </span>
                                                        {result.prediction}
                                                    </td>
                                                    <td>
                                                        <button 
                                                            className="view-details-btn"
                                                            onClick={() => showResultDetails(result)}
                                                        >
                                                            View Details
                                                        </button>
                                                    </td>
                                                    <td>{result.reason || "No explanation available"}</td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                                
                                {/* Details popup for time series entries */}
                                {selectedResult && (
                                    <div className="details-overlay">
                                        <div className="details-modal">
                                            <div className="details-header">
                                                <h3>Traffic Details</h3>
                                                <button className="close-btn" onClick={() => setSelectedResult(null)}>×</button>
                                            </div>
                                            <div className="details-content">
                                                <div className={`status-badge ${selectedResult.prediction.toLowerCase()}`}>
                                                    {selectedResult.prediction === "Malicious" ? "⚠️ Malicious" : "✅ Normal"}
                                                </div>
                                                <p><strong>Time:</strong> {selectedResult.time}</p>
                                                {renderDataValues(selectedResult.data)}
                                                <div className="details-reason">
                                                    <h4>Analysis:</h4>
                                                    <p>{selectedResult.reason}</p>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                )}
                
                {activeTab === "batch" && (
                    <div className="tab-content">
                        <div className="action-buttons">
                            <button 
                                onClick={() => generateMultipleRandomPredictions(10)} 
                                disabled={isLoading}
                                className="batch-button"
                            >
                                📊 Run 10 Random Predictions
                            </button>
                        </div>
                        
                        {isLoading && (
                            <div className="loading">
                                <div className="loader"></div>
                                <p>Running batch analysis...</p>
                            </div>
                        )}

                        {randomResults.length > 0 && !isContinuous && (
                            <div className="visualization-section">
                                <h2>Batch Analysis Results</h2>
                                
                                <div className="charts-row">
                                    <div className="chart-container half-width">
                                        <h3>Results Distribution</h3>
                                        <ResponsiveContainer width="100%" height={300}>
                                            <PieChart>
                                                <Pie
                                                    data={randomResults[randomResults.length-1].chartData}
                                                    cx="50%"
                                                    cy="50%"
                                                    labelLine={false}
                                                    outerRadius={100}
                                                    fill="#8884d8"
                                                    dataKey="value"
                                                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                                                >
                                                    {randomResults[randomResults.length-1].chartData.map((entry, index) => (
                                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                                    ))}
                                                </Pie>
                                                <Tooltip formatter={(value) => [value, "Count"]} />
                                            </PieChart>
                                        </ResponsiveContainer>
                                    </div>
                                    
                                    <div className="chart-container half-width">
                                        <h3>Results Distribution</h3>
                                        <ResponsiveContainer width="100%" height={300}>
                                            <BarChart data={randomResults[randomResults.length-1].chartData}>
                                                <CartesianGrid strokeDasharray="3 3" />
                                                <XAxis dataKey="name" />
                                                <YAxis label={{ value: 'Count', angle: -90, position: 'insideLeft' }} />
                                                <Tooltip />
                                                <Legend />
                                                <Bar dataKey="value" name="Number of Predictions" fill="#8884d8">
                                                    {randomResults[randomResults.length-1].chartData.map((entry, index) => (
                                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                                    ))}
                                                </Bar>
                                            </BarChart>
                                        </ResponsiveContainer>
                                    </div>
                                </div>
                                
                                <h3>Detailed Results</h3>
                                <div className="results-table">
                                    <table>
                                        <thead>
                                            <tr>
                                                <th>#</th>
                                                <th>Status</th>
                                                <th>Actions</th>
                                                <th>Reason</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {randomResults.slice(0, -1).map((result) => (
                                                <tr key={result.id} className={result.prediction.toLowerCase()}>
                                                    <td>{result.id}</td>
                                                    <td className="status-cell">
                                                        <span className={`status-icon ${result.prediction.toLowerCase()}`}>
                                                            {result.prediction === "Malicious" ? "⚠️" : "✅"}
                                                        </span>
                                                        {result.prediction}
                                                    </td>
                                                    <td>
                                                        <button 
                                                            className="view-details-btn"
                                                            onClick={() => showResultDetails(result)}
                                                        >
                                                            View Details
                                                        </button>
                                                    </td>
                                                    <td>{result.reason}</td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                                
                                {/* Details popup for batch entries */}
                                {selectedResult && (
                                    <div className="details-overlay">
                                        <div className="details-modal">
                                            <div className="details-header">
                                                <h3>Traffic Details</h3>
                                                <button className="close-btn" onClick={() => setSelectedResult(null)}>×</button>
                                            </div>
                                            <div className="details-content">
                                                <div className={`status-badge ${selectedResult.prediction.toLowerCase()}`}>
                                                    {selectedResult.prediction === "Malicious" ? "⚠️ Malicious" : "✅ Normal"}
                                                </div>
                                                {selectedResult.time && <p><strong>Time:</strong> {selectedResult.time}</p>}
                                                {renderDataValues(selectedResult.data)}
                                                <div className="details-reason">
                                                    <h4>Analysis:</h4>
                                                    <p>{selectedResult.reason}</p>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                )}
                
                {activeTab === "help" && (
                    <div className="tab-content help-content">
                        <h2>Getting Started with Network Guardian</h2>
                        <div className="help-section">
                            <h3>Understanding Network Traffic Analysis</h3>
                            <p>
                                Network Guardian analyzes various parameters of network traffic to detect potential
                                malicious activities. Our machine learning model examines patterns in your network
                                data to identify suspicious behavior.
                            </p>
                        </div>
                        
                        <div className="help-section">
                            <h3>Feature Descriptions</h3>
                            <div className="feature-list">
                                <div className="feature-item">
                                    <h4>Destination Port</h4>
                                    <p>The port number on the destination device to which the traffic is directed.</p>
                                </div>
                                <div className="feature-item">
                                    <h4>Flow Duration</h4>
                                    <p>The total time of the network flow in milliseconds.</p>
                                </div>
                                <div className="feature-item">
                                    <h4>Total Forward/Backward Packets</h4>
                                    <p>Count of packets in the forward/backward direction of the flow.</p>
                                </div>
                                <div className="feature-item">
                                    <h4>Flow Bytes/Packets per Second</h4>
                                    <p>Rate of bytes/packets transferred in the flow per second.</p>
                                </div>
                                <div className="feature-item">
                                    <h4>Packet Length (Max, Mean, Std)</h4>
                                    <p>Statistics about packet sizes in the flow.</p>
                                </div>
                                <div className="feature-item">
                                    <h4>Flag Counts (SYN, ACK, FIN)</h4>
                                    <p>Number of packets with specific TCP flags set.</p>
                                </div>
                            </div>
                        </div>
                        
                        <div className="help-section">
                            <h3>Using the Application</h3>
                            <div className="usage-instructions">
                                <h4>Manual Input Mode</h4>
                                <p>
                                    Enter specific network traffic parameters to analyze individual flows.
                                    Use the "Generate Random Values" button to quickly populate the form
                                    with test data.
                                </p>
                                
                                <h4>Continuous Monitoring</h4>
                                <p>
                                    Enable real-time monitoring simulation with randomly generated traffic
                                    parameters. The system will generate and analyze new traffic patterns
                                    every 5 seconds and display trends over time.
                                </p>
                                
                                <h4>Batch Analysis</h4>
                                <p>
                                    Run multiple predictions at once to analyze trends and distribution
                                    of traffic types. This helps identify pattern distributions across
                                    multiple network flows.
                                </p>
                            </div>
                        </div>
                        
                        <div className="help-section">
                            <h3>Understanding Results</h3>
                            <div className="results-explanation">
                                <div className="result-type normal">
                                    <h4>✅ Normal Traffic</h4>
                                    <p>
                                        Traffic patterns that match expected legitimate behavior.
                                        Typically exhibits balanced metrics and follows standard
                                        network protocol patterns.
                                    </p>
                                </div>
                                
                                <div className="result-type malicious">
                                    <h4>⚠️ Malicious Traffic</h4>
                                    <p>
                                        Traffic patterns that show signs of potential attacks or
                                        suspicious activity. May include unusual port usage, abnormal
                                        packet distributions, or unusual flag combinations.
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </div>
            
            <footer className="app-footer">
                <p>Network Guardian • Advanced Network Traffic Analysis System</p>
                <p className="disclaimer">This is a demonstration application. Connect to a real API endpoint for production use.</p>
            </footer>
        </div>
    );
}

export default App;