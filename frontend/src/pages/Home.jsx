import { useNavigate } from "react-router-dom";

import { motion } from "framer-motion";

import {
    Brain,
    Activity,
    BarChart3,
    ShieldCheck
} from "lucide-react";


export default function Home() {

    const navigate = useNavigate();

    return (

        <div className="page-container">

            <motion.div
                className="glass-card"
                initial={{ opacity: 0, y: 40 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8 }}
            >

                {/* =====================================
                    HERO
                ===================================== */}

                <div className="hero-title">

                    Disease Progression Volatility Index :
                    <br />

                    <span className="gradient-text">

                      in Parkinson’s Disease

                    </span>

                </div>

                <div className="hero-description">

                    An Instability-Driven Computational
                    Framework for Quantifying Parkinson’s
                    Disease Progression Dynamics using
                    longitudinal clinical data, DPVI
                    features, explainable AI analytics,
                    temporal volatility modeling,
                    risk stratification, and machine
                    learning-based progression analysis.

                </div>


                {/* =====================================
                    FEATURES
                ===================================== */}

                <div
                    className="metrics-grid"
                    style={{ marginBottom: "40px" }}
                >

                    <div className="metric-card">

                        <Brain
                            size={42}
                            style={{
                                marginBottom: "16px",
                                color: "#60a5fa"
                            }}
                        />

                        <div className="metric-title">

                            DPVI Intelligence

                        </div>

                        <div>

                            Quantifies instability,
                            volatility, entropy,
                            spikes, and progression
                            reversals.

                        </div>

                    </div>

                    <div className="metric-card">

                        <Activity
                            size={42}
                            style={{
                                marginBottom: "16px",
                                color: "#818cf8"
                            }}
                        />

                        <div className="metric-title">

                            Progression Analysis

                        </div>

                        <div>

                            Tracks fluctuating
                            longitudinal symptom
                            progression behavior
                            over time.

                        </div>

                    </div>

                    <div className="metric-card">

                        <BarChart3
                            size={42}
                            style={{
                                marginBottom: "16px",
                                color: "#38bdf8"
                            }}
                        />

                        <div className="metric-title">

                            Explainable Analytics

                        </div>

                        <div>

                            Provides insights,
                            confusion matrices,
                            model metrics, and
                            feature importance.

                        </div>

                    </div>

                    <div className="metric-card">

                        <ShieldCheck
                            size={42}
                            style={{
                                marginBottom: "16px",
                                color: "#c084fc"
                            }}
                        />

                        <div className="metric-title">

                            Clinical Decision Support

                        </div>

                        <div>

                            Helps identify stable,
                            moderate, and high-risk
                            progression trajectories.

                        </div>

                    </div>

                </div>


                {/* =====================================
                    CTA BUTTON
                ===================================== */}

                <button
                    className="primary-btn"
                    onClick={() => navigate("/upload")}
                >

                    Start DPVI Analysis

                </button>

            </motion.div>

        </div>
    );
}