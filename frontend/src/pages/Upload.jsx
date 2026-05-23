import { useState } from "react";

import { useNavigate } from "react-router-dom";

import { motion } from "framer-motion";

import {
    UploadCloud,
    FileArchive,
    CheckCircle2,
    AlertCircle
} from "lucide-react";

import {
    uploadDataset,
    startPipeline
} from "../api";


export default function Upload() {

    const navigate = useNavigate();

    const [file, setFile] = useState(null);

    const [loading, setLoading] = useState(false);

    const [message, setMessage] = useState("");

    const [error, setError] = useState(false);


    /* ============================================
       HANDLE FILE
    ============================================ */

    const handleFileChange = (e) => {

        const selectedFile = e.target.files[0];

        if (!selectedFile) return;

        if (!selectedFile.name.endsWith(".zip")) {

            setError(true);

            setMessage("Please upload a ZIP file");

            return;
        }

        setFile(selectedFile);

        setError(false);

        setMessage("ZIP file selected successfully");
    };


    /* ============================================
       HANDLE UPLOAD
    ============================================ */

    const handleUpload = async () => {

        if (!file) {

            setError(true);

            setMessage("Please select a ZIP file");

            return;
        }

        try {

            setLoading(true);

            setError(false);

            setMessage("Uploading dataset ZIP...");

            const formData = new FormData();

            formData.append("file", file);

            // --------------------------------------
            // UPLOAD ZIP
            // --------------------------------------

            const uploadResponse = await uploadDataset(
                formData
            );

            if (!uploadResponse.success) {

                throw new Error(
                    uploadResponse.message
                );
            }

            setMessage(
                "Dataset uploaded successfully"
            );

            // --------------------------------------
            // START PIPELINE
            // --------------------------------------

            const pipelineResponse =
                await startPipeline();

            if (!pipelineResponse.success) {

                throw new Error(
                    pipelineResponse.message
                );
            }

            setMessage(
                "Processing pipeline started"
            );

            // --------------------------------------
            // REDIRECT
            // --------------------------------------

            setTimeout(() => {

                navigate("/processing");

            }, 1200);

        } catch (err) {

            setError(true);

            setMessage(
                err.message ||
                "Upload failed"
            );

        } finally {

            setLoading(false);
        }
    };


    return (

        <div className="page-container">

            <motion.div
                className="glass-card"
                initial={{ opacity: 0, y: 40 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.7 }}
            >

                {/* =====================================
                    TITLE
                ===================================== */}

                <div className="hero-title">

                    Upload Parkinson’s
                    <br />

                    <span className="gradient-text">

                        Longitudinal Dataset

                    </span>

                </div>

                <div className="hero-description">

                    Upload the compressed ZIP dataset
                    containing motor, non-motor,
                    biospecimen, digital sensor,
                    and medical history data folders.
                    The system will automatically
                    replace the current dataset,
                    process the longitudinal records,
                    compute DPVI features,
                    perform risk analysis,
                    train the models,
                    and generate explainable
                    progression insights.

                </div>


                {/* =====================================
                    UPLOAD BOX
                ===================================== */}

                <div className="upload-box">

                    <FileArchive
                        size={70}
                        style={{
                            marginBottom: "20px",
                            color: "#60a5fa"
                        }}
                    />

                    <h2
                        style={{
                            marginBottom: "12px"
                        }}
                    >

                        Upload data.zip

                    </h2>

                    <p
                        style={{
                            color: "#cbd5e1",
                            marginBottom: "20px"
                        }}
                    >

                        Supported format:
                        ZIP containing all dataset folders

                    </p>

                    <input
                        type="file"
                        accept=".zip"
                        onChange={handleFileChange}
                        className="upload-input"
                    />

                    <div
                        style={{
                            marginTop: "25px"
                        }}
                    >

                        <button
                            className="primary-btn"
                            onClick={handleUpload}
                            disabled={loading}
                        >

                            {
                                loading
                                    ? "Processing..."
                                    : "Upload & Start Analysis"
                            }

                        </button>

                    </div>

                </div>


                {/* =====================================
                    STATUS MESSAGE
                ===================================== */}

                {
                    message && (

                        <div
                            style={{
                                marginTop: "30px",
                                padding: "18px",
                                borderRadius: "16px",
                                background: error
                                    ? "rgba(239,68,68,0.12)"
                                    : "rgba(34,197,94,0.12)",
                                border: error
                                    ? "1px solid rgba(239,68,68,0.3)"
                                    : "1px solid rgba(34,197,94,0.3)",
                                display: "flex",
                                alignItems: "center",
                                gap: "12px"
                            }}
                        >

                            {
                                error ? (

                                    <AlertCircle
                                        size={24}
                                        color="#fca5a5"
                                    />

                                ) : (

                                    <CheckCircle2
                                        size={24}
                                        color="#86efac"
                                    />
                                )
                            }

                            <span>

                                {message}

                            </span>

                        </div>
                    )
                }


                {/* =====================================
                    INFO SECTION
                ===================================== */}

                <div
                    className="metrics-grid"
                    style={{
                        marginTop: "40px"
                    }}
                >

                    <div className="metric-card">

                        <div className="metric-title">

                            Dataset Processing

                        </div>

                        <div>

                            Automatic extraction,
                            validation, preprocessing,
                            and feature engineering.

                        </div>

                    </div>

                    <div className="metric-card">

                        <div className="metric-title">

                            DPVI Computation

                        </div>

                        <div>

                            Computes entropy,
                            spikes, temporal change,
                            variability, and reversals.

                        </div>

                    </div>

                    <div className="metric-card">

                        <div className="metric-title">

                            Model Training

                        </div>

                        <div>

                            DPVI and weighted
                            DPVI training with
                            explainable analytics.

                        </div>

                    </div>

                </div>

            </motion.div>

        </div>
    );
}