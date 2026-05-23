import { useEffect, useState } from "react";

import { useNavigate } from "react-router-dom";

import { motion } from "framer-motion";

import {
    Activity,
    BarChart3,
    Brain,
    ShieldAlert
} from "lucide-react";

import {
    getPredictionResults,
    getPipelineStatus,
    getProgressLogs
} from "../api";

import MetricCard from "../components/MetricCard";

import InsightBox from "../components/InsightBox";


export default function Prediction() {

    const navigate = useNavigate();

    const [results, setResults] = useState(null);

    const [logs, setLogs] = useState([]);

    const [running, setRunning] = useState(true);


    useEffect(() => {

        const fetchLiveData = async () => {

            try {

                const resultResponse = await getPredictionResults();

                if (
                    resultResponse.success &&
                    resultResponse.results
                ) {

                    setResults(resultResponse);
                }

                const progressResponse = await getProgressLogs();

                if (progressResponse.success) {

                    setLogs(progressResponse.progress);
                }

                const statusResponse = await getPipelineStatus();

                setRunning(statusResponse.running);

            } catch (error) {

                console.error(error);
            }
        };

        fetchLiveData();

        const interval = setInterval(fetchLiveData, 600000);

        return () => clearInterval(interval);

    }, []);


    if (!results || !results.prediction) {

        return (

            <div className="page-container">

                <div className="glass-card">

                    <div className="hero-title">

                        Preparing
                        <br />

                        <span className="gradient-text">

                            Prediction Results

                        </span>

                    </div>

                    <div className="hero-description">

                        {
                            running
                                ? "The DPVI pipeline is still processing. Current backend activity is shown below."
                                : "Processing is completed, but results are still being prepared."
                        }

                    </div>

                    <div className="progress-list">

                        {
                            logs.length === 0 ? (

                                <div className="progress-item">

                                    Waiting for backend processing messages...

                                </div>

                            ) : (

                                logs.slice(-12).map((log, index) => (

                                    <div
                                        key={index}
                                        className="progress-item"
                                    >

                                        <strong>[{log.time}]</strong> {log.message}

                                    </div>
                                ))
                            )
                        }

                    </div>

                </div>

            </div>
        );
    }


    const prediction = results.prediction;

    const summary = results.summary || {};


    return (

        <div className="page-container">

            <motion.div
                className="glass-card"
                initial={{ opacity: 0, y: 35 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.7 }}
            >

                <div className="hero-title">

                    Prediction
                    <br />

                    <span className="gradient-text">

                        Results

                    </span>

                </div>

                <div className="hero-description">

                    The system completed  DPVI and weighted DPVI
                    processing. This screen summarizes the dynamically
                    selected best pipeline, DPVI score, instability category,
                    and best-performing model.

                </div>


                <div className="metrics-grid">

                    <MetricCard
                        title="Average Accuracy Elevation"
                        value={
                            prediction.average_accuracy_elevation_percent || "NA"
                        }
                    />

                    <MetricCard
                        title="DPVI Score"
                        value={
                            prediction.dpvi_score ?? "NA"
                        }
                    />

                    <MetricCard
                        title="Best Model"
                        value={
                            prediction.best_model || "NA"
                        }
                    />

                    <MetricCard
                        title="Best Accuracy"
                        value={
                            prediction.best_accuracy_percent || "NA"
                        }
                    />
                    <MetricCard
    title="Baseline Accuracy"
    value={
        prediction.baseline_accuracy_percent || "NA"
    }
/>

<MetricCard
    title="Accuracy Elevation"
    value={
        prediction.accuracy_elevation_percent || "NA"
    }
/>

                </div>


                <div
                    style={{
                        marginTop: "30px"
                    }}
                >

                    <h2
                        style={{
                            marginBottom: "12px"
                        }}
                    >

                        Risk Classification

                    </h2>

                    <div
                        className={
                            prediction.risk_level === "High Instability"
                                ? "risk-badge risk-high"
                                : prediction.risk_level === "Low Instability"
                                    ? "risk-badge risk-stable"
                                    : "risk-badge risk-moderate"
                        }
                    >

                        {prediction.risk_level || "NA"}

                    </div>

                </div>


                <div
                    className="prediction-detail-grid"
                >
                    
                    
                    <div className="metric-card prediction-small-card">

                        <Activity
                            size={36}
                            color="#60a5fa"
                            style={{ marginBottom: "12px" }}
                        />

                        <div className="metric-title">

                            Selected Pipeline

                        </div>

                        <div className="metric-value">

                            {prediction.selected_pipeline || summary.selected_pipeline || "NA"}

                        </div>

                    </div>


                    <div className="metric-card prediction-small-card">

                        <Brain
                            size={36}
                            color="#818cf8"
                            style={{ marginBottom: "12px" }}
                        />

                        <div className="metric-title">

                             DPVI Dataset

                        </div>

                        <div className="metric-value">

                            {prediction._dataset_shape || "NA"}

                        </div>

                    </div>


                    <div className="metric-card prediction-small-card">

                        <Brain
                            size={36}
                            color="#818cf8"
                            style={{ marginBottom: "12px" }}
                        />

                        <div className="metric-title">

                            Weighted DPVI Dataset

                        </div>

                        <div className="metric-value">

                            {prediction.weighted_dataset_shape || "NA"}

                        </div>

                    </div>


                    <div className="metric-card prediction-wide-card">

                        <ShieldAlert
                            size={36}
                            color="#fbbf24"
                            style={{ marginBottom: "12px" }}
                        />

                        <div className="metric-title">

                            Clinical Interpretation

                        </div>

                        <div
                            style={{
                                color: "#dbeafe",
                                lineHeight: "1.6"
                            }}
                        >

                            {prediction.clinical_interpretation || "NA"}

                        </div>

                    </div>


                    <div className="metric-card prediction-wide-card">

                        <BarChart3
                            size={36}
                            color="#c084fc"
                            style={{ marginBottom: "12px" }}
                        />

                        <div className="metric-title">

                            DPVI Contribution

                        </div>

                        <div
                            style={{
                                color: "#dbeafe",
                                lineHeight: "1.6"
                            }}
                        >

                            {prediction.dpvi_contribution || "NA"}

                        </div>

                    </div>

                    
<div className="metric-card prediction-small-card">

    <BarChart3
        size={36}
        color="#c084fc"
        style={{ marginBottom: "12px" }}
    />

    <div className="metric-title">

        GridSearchCV Best Parameters

    </div>

    <div
        style={{
            color: "#dbeafe",
            lineHeight: "1.8",
            fontSize: "15px"
        }}
    >

        {
            prediction.tuned_best_params &&
            Object.keys(prediction.tuned_best_params).length > 0
                ? Object.entries(prediction.tuned_best_params).map(
                    ([key, value]) => (
                        <div key={key}>
                            <strong>{key}</strong>: {String(value)}
                        </div>
                    )
                )
                : "NA"
        }

    </div>

</div>

                </div>


                <InsightBox
                    title="Prediction Insights"
                    insights={prediction.prediction_insights || []}
                />


                <div
                    style={{
                        marginTop: "35px",
                        display: "flex",
                        gap: "18px",
                        flexWrap: "wrap"
                    }}
                >

                    <button
                        className="primary-btn"
                        onClick={() => navigate("/analysis")}
                    >

                        View  Analysis Dashboard

                    </button>

                    <button
                        className="primary-btn"
                        onClick={() => navigate("/upload")}
                    >

                        Upload New Dataset

                    </button>

                </div>

            </motion.div>

        </div>
    );
}