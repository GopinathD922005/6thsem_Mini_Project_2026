import { useEffect, useState } from "react";

import { motion } from "framer-motion";

import {
    Bar,
    BarChart,
    CartesianGrid,
    Cell,
    ResponsiveContainer,
    Tooltip,
    XAxis,
    YAxis
} from "recharts";

import { getAnalysisResults } from "../api";

import MetricCard from "../components/MetricCard";

import ChartCard from "../components/ChartCard";

import ResultTable from "../components/ResultTable";

import InsightBox from "../components/InsightBox";


export default function Analysis() {

    const [results, setResults] = useState(null);


    useEffect(() => {

        const fetchResults = async () => {

            try {

                const response = await getAnalysisResults();

                if (response.success) {

                    setResults(response);
                }

            } catch (error) {

                console.error(error);
            }
        };

        fetchResults();

    }, []);


    if (!results || !results.analysis) {

        return (

            <div className="page-container">

                <div className="glass-card">

                    <h2>Loading analysis dashboard...</h2>

                </div>

            </div>
        );
    }


    const analysis = results.analysis;

    const metrics = analysis.metrics || {};

    const ablation = analysis.ablation || {};

    const insights = analysis.explainability_insights || [];

    const featureImportance = analysis.feature_importance || [];

    const confusion = analysis.confusion_matrix || {};


    const metricChartData = [

        {
            name: "Accuracy",
            value: metrics.accuracy || 0
        },

        {
            name: "Precision",
            value: metrics.precision || 0
        },

        {
            name: "Recall",
            value: metrics.recall || 0
        },

        {
            name: "F1",
            value: metrics.f1_score || 0
        },

        {
            name: "ROC-AUC",
            value: metrics.roc_auc || 0
        }
    ];


    const ablationChartData = [

        {
            name: "Baseline",
            accuracy: ablation.baseline_accuracy || 0
        },

        {
            name: "DPVI",
            accuracy: ablation.dpvi_accuracy || 0
        }
    ];


    const metricColors = [
        "#38bdf8",
        "#22c55e",
        "#facc15",
        "#a78bfa",
        "#f97316"
    ];


    const ablationColors = [
        "#64748b",
        "#22c55e"
    ];


    const percentValue = (value) => {

        if (value === undefined || value === null) {
            return "NA";
        }

        return (Number(value) * 100).toFixed(2);
    };


    const decimalValue = (value) => {

        if (value === undefined || value === null) {
            return "NA";
        }

        return Number(value).toFixed(4);
    };


    return (

        <div className="page-container">

            <motion.div
                className="glass-card"
                initial={{ opacity: 0, y: 35 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.7 }}
            >

                <div className="hero-title">

                    Analysis
                    <br />

                    <span className="gradient-text">

                        Dashboard

                    </span>

                </div>

                <div className="hero-description">

                    Comprehensive DPVI analytics dashboard containing
                    model comparison, confusion matrix, ablation analysis,
                    explainability metrics, feature importance, and
                    longitudinal progression insights.

                </div>


                <div className="metrics-grid">

                    <MetricCard
                        title="Accuracy"
                        value={percentValue(metrics.accuracy)}
                        suffix="%"
                    />

                    <MetricCard
                        title="Precision"
                        value={percentValue(metrics.precision)}
                        suffix="%"
                    />

                    <MetricCard
                        title="Recall"
                        value={percentValue(metrics.recall)}
                        suffix="%"
                    />

                    <MetricCard
                        title="F1 Score"
                        value={percentValue(metrics.f1_score)}
                        suffix="%"
                    />

                    <MetricCard
                        title="ROC-AUC"
                        value={decimalValue(metrics.roc_auc)}
                    />

                    <MetricCard
                        title="R² Score"
                        value={decimalValue(metrics.r2_score)}
                    />

                </div>


                <div className="chart-grid">

                    <ChartCard title="Model Performance Metrics">

                        <ResponsiveContainer
                            width="100%"
                            height={320}
                        >

                            <BarChart data={metricChartData}>

                                <CartesianGrid strokeDasharray="3 3" />

                                <XAxis dataKey="name" />

                                <YAxis domain={[0, 1]} />

                                <Tooltip />

                                <Bar
                                    dataKey="value"
                                    radius={[10, 10, 0, 0]}
                                >

                                    {
                                        metricChartData.map((entry, index) => (

                                            <Cell
                                                key={`metric-cell-${index}`}
                                                fill={metricColors[index]}
                                            />
                                        ))
                                    }

                                </Bar>

                            </BarChart>

                        </ResponsiveContainer>

                    </ChartCard>


                    <ChartCard title="Baseline vs DPVI Accuracy">

                        <ResponsiveContainer
                            width="100%"
                            height={320}
                        >

                            <BarChart data={ablationChartData}>

                                <CartesianGrid strokeDasharray="3 3" />

                                <XAxis dataKey="name" />

                                <YAxis domain={[0, 1]} />

                                <Tooltip />

                                <Bar
                                    dataKey="accuracy"
                                    radius={[10, 10, 0, 0]}
                                >

                                    {
                                        ablationChartData.map((entry, index) => (

                                            <Cell
                                                key={`ablation-cell-${index}`}
                                                fill={ablationColors[index]}
                                            />
                                        ))
                                    }

                                </Bar>

                            </BarChart>

                        </ResponsiveContainer>

                    </ChartCard>

                </div>


                <div
                    style={{
                        marginTop: "40px"
                    }}
                >

                    <h2
                        style={{
                            marginBottom: "20px"
                        }}
                    >

                        Confusion Matrix

                    </h2>

                    <ResultTable
                        headers={[
                            "",
                            "Predicted Positive",
                            "Predicted Negative"
                        ]}
                        rows={[
                            [
                                "Actual Positive",
                                confusion.tp || 0,
                                confusion.fn || 0
                            ],
                            [
                                "Actual Negative",
                                confusion.fp || 0,
                                confusion.tn || 0
                            ]
                        ]}
                    />

                </div>


                <div
                    style={{
                        marginTop: "40px"
                    }}
                >

                    <h2
                        style={{
                            marginBottom: "20px"
                        }}
                    >

                        Feature Importance

                    </h2>

                    <ResultTable
                        headers={[
                            "Feature",
                            "Importance"
                        ]}
                        rows={
                            featureImportance.length > 0
                                ? featureImportance.map((item) => [
                                    item.feature,
                                    decimalValue(item.importance)
                                ])
                                : [
                                    [
                                        "No feature importance available",
                                        "NA"
                                    ]
                                ]
                        }
                    />

                </div>


                <div
                    style={{
                        marginTop: "40px"
                    }}
                >

                    <h2
                        style={{
                            marginBottom: "20px"
                        }}
                    >

                        Ablation Analysis

                    </h2>

                    <ResultTable
                        headers={[
                            "Metric",
                            "Value"
                        ]}
                        rows={[
                            [
                                "Baseline Accuracy",
                                `${percentValue(ablation.baseline_accuracy)}%`
                            ],
                            [
                                "DPVI Accuracy",
                                `${percentValue(ablation.dpvi_accuracy)}%`
                            ],
                            [
                                "Accuracy Improvement",
                                `${percentValue(ablation.accuracy_improvement)}%`
                            ],
                            [
                                "Baseline ROC-AUC",
                                decimalValue(ablation.baseline_roc_auc)
                            ],
                            [
                                "DPVI ROC-AUC",
                                decimalValue(ablation.dpvi_roc_auc)
                            ],
                            [
                                "ROC-AUC Improvement",
                                `${percentValue(ablation.roc_auc_improvement)}%`
                            ],
                            [
                                "Average Accuracy Elevation",
                                ablation.average_accuracy_elevation_percent || "NA"
                            ]
                        ]}
                    />

                </div>


                <InsightBox
                    title="Explainability Insights"
                    insights={insights}
                />


                <div
                    className="insight-box"
                    style={{
                        marginTop: "35px"
                    }}
                >

                    <div className="insight-title">

                        Clinical Interpretation

                    </div>

                    <div
                        style={{
                            lineHeight: "1.8",
                            color: "#dbeafe"
                        }}
                    >

                        {
                            analysis.clinical_interpretation
                                ? analysis.clinical_interpretation
                                    .split("\n\n")
                                    .map((paragraph, index) => (

                                        <p
                                            key={index}
                                            style={{
                                                marginBottom: "16px"
                                            }}
                                        >

                                            {paragraph}

                                        </p>
                                    ))
                                : "No clinical interpretation available."
                        }

                    </div>

                </div>

            </motion.div>

        </div>
    );
}