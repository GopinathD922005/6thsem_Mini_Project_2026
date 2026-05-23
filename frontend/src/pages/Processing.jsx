import { useEffect, useRef, useState } from "react";

import { useNavigate } from "react-router-dom";

import { motion } from "framer-motion";

import {
    LoaderCircle,
    CheckCircle2,
    BrainCircuit
} from "lucide-react";

import {
    getProgressLogs,
    getPipelineStatus
} from "../api";

import ProgressTimeline from "../components/ProgressTimeline";


export default function Processing() {

    const navigate = useNavigate();

    const [logs, setLogs] = useState([]);

    const [running, setRunning] = useState(true);

    const redirectedRef = useRef(false);
    /* ============================================
       FETCH LOGS
    ============================================ */

    const fetchLogs = async () => {

        try {

            const response =
                await getProgressLogs();

            if (response.success) {

                setLogs(response.progress);
            }

        } catch (error) {

            console.error(error);
        }
    };


    /* ============================================
       FETCH STATUS
    ============================================ */

    const fetchStatus = async () => {

        try {

            const response =
                await getPipelineStatus();

            setRunning(response.running);

            // ------------------------------------
            // IF COMPLETED
            // ------------------------------------

            if (!response.running) {

                setTimeout(() => {

                    navigate("/prediction");

                }, 2500);
            }

        } catch (error) {

            console.error(error);
        }
    };


    /* ============================================
       LIVE POLLING
    ============================================ */

    useEffect(() => {

        fetchLogs();

        fetchStatus();

        const interval = setInterval(() => {

            fetchLogs();

            fetchStatus();

        }, 600000);

        return () => clearInterval(interval);

    }, []);


    return (

        <div className="page-container">

            <motion.div
                className="glass-card"
                initial={{ opacity: 0, y: 35 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.7 }}
            >

                {/* =====================================
                    HEADER
                ===================================== */}

                <div
                    style={{
                        display: "flex",
                        alignItems: "center",
                        gap: "18px",
                        marginBottom: "20px"
                    }}
                >

                    {
                        running ? (

                            <LoaderCircle
                                size={44}
                                className="spin-loader"
                                color="#60a5fa"
                            />

                        ) : (

                            <CheckCircle2
                                size={44}
                                color="#4ade80"
                            />
                        )
                    }

                    <div>

                        <div className="processing-title">

                            {
                                running
                                    ? "Processing Longitudinal DPVI Pipeline"
                                    : "Pipeline Completed Successfully"
                            }

                        </div>

                        <div
                            style={{
                                color: "#cbd5e1"
                            }}
                        >

                            {
                                running
                                    ? "Computing DPVI features, training models, generating insights, and preparing analytics dashboard..."
                                    : "Redirecting to prediction dashboard..."
                            }

                        </div>

                    </div>

                </div>


                {/* =====================================
                    LIVE STATUS CARD
                ===================================== */}

                <div
                    className="metric-card"
                    style={{
                        marginBottom: "30px"
                    }}
                >

                    <div
                        style={{
                            display: "flex",
                            alignItems: "center",
                            gap: "15px"
                        }}
                    >

                        <BrainCircuit
                            size={36}
                            color="#818cf8"
                        />

                        <div>

                            <div
                                className="metric-title"
                            >

                                Current Processing Status

                            </div>

                            <div
                                style={{
                                    fontSize: "18px",
                                    fontWeight: "600"
                                }}
                            >

                                {
                                    running
                                        ? "DPVI pipeline is actively processing..."
                                        : "All processing stages completed."
                                }

                            </div>

                        </div>

                    </div>

                </div>


                {/* =====================================
                    TIMELINE
                ===================================== */}

                <ProgressTimeline logs={logs} />


                {/* =====================================
                    PROCESSING INSIGHTS
                ===================================== */}

                <div
                    className="metrics-grid"
                    style={{
                        marginTop: "35px"
                    }}
                >

                    <div className="metric-card">

                        <div className="metric-title">

                            DPVI Analysis

                        </div>

                        <div>

                            Generating 188-column
                            longitudinal DPVI
                            feature representation.

                        </div>

                    </div>

                    <div className="metric-card">

                        <div className="metric-title">

                            Weighted DPVI Optimization

                        </div>

                        <div>

                            Compressing longitudinal
                            volatility features into
                            optimized 64-column space.

                        </div>

                    </div>

                    <div className="metric-card">

                        <div className="metric-title">

                            Explainable Analytics

                        </div>

                        <div>

                            Preparing feature importance,
                            confusion matrix,
                            cross-validation,
                            and ablation metrics.

                        </div>

                    </div>

                </div>

            </motion.div>

        </div>
    );
}