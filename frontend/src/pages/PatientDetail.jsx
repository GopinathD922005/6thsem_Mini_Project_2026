import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { getPatientDetail } from "../api";
import PatientLineGraph from "../components/PatientLineGraph";
import MultiFeatureGraph from "../components/MultiFeatureGraph";
import StatusBadge from "../components/StatusBadge";

export default function PatientDetail() {
    const { patno } = useParams();

    const [patient, setPatient] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const loadPatient = async () => {
            try {
                const data = await getPatientDetail(patno);
                setPatient(data.patient);
            } catch (error) {
                console.error("Failed to load patient detail", error);
            } finally {
                setLoading(false);
            }
        };

        loadPatient();
    }, [patno]);

    if (loading) {
        return (
            <div className="page-shell">
                <div className="glass-card">
                    Loading patient details...
                </div>
            </div>
        );
    }

    if (!patient) {
        return (
            <div className="page-shell">
                <div className="glass-card">
                    Patient data not found.
                </div>
            </div>
        );
    }

    return (
        <div className="page-shell">
            <div className="page-header">
                <h1>Patient Detailed Progression</h1>
                <p>PATNO: {patient.patno}</p>
            </div>

            <div className="glass-card detail-summary-grid">
                <div>
                    <p className="muted-label">Actual Status</p>
                    <StatusBadge label={patient.actual_status} type="status" />
                </div>

<div>
    <p className="muted-label">DPVI Prediction Status</p>
    <StatusBadge
        label={patient.dpvi_predicted_status}
        type="status"
    />
</div>

<div>
    <p className="muted-label">Baseline Prediction Status</p>
    <StatusBadge
        label={patient.baseline_predicted_status}
        type="status"
    />
</div>

<div>
    <p className="muted-label">DPVI Prediction Result</p>
    <StatusBadge
        label={patient.dpvi_prediction_result}
        type="result"
    />
</div>

<div>
    <p className="muted-label">Baseline Prediction Result</p>
    <StatusBadge
        label={patient.baseline_prediction_result}
        type="result"
    />
</div>

                <div>
                    <p className="muted-label">Instability</p>
                    <StatusBadge label={patient.instability} type="instability" />
                </div>

                <div>
                    <p className="muted-label">DPVI Score</p>
                    <h3>{patient.dpvi_score ?? "N/A"}</h3>
                </div>

                <div>
                    <p className="muted-label">Visits</p>
                    <h3>{patient.visit_count}</h3>
                </div>

                <div>
                    <p className="muted-label">Primary Volatility Feature</p>
                    <h3>{patient.primary_volatility_feature}</h3>
                </div>

                <div>
                    <p className="muted-label">Prediction Confidence</p>
                    <h3>
                        {patient.prediction_confidence
                            ? `${(patient.prediction_confidence * 100).toFixed(2)}%`
                            : "N/A"}
                    </h3>
                </div>
            </div>

            <div className="glass-card">
                <h2>Primary Disease Progression Graph</h2>
                <PatientLineGraph
                    feature={patient.primary_graph?.feature}
                    points={patient.primary_graph?.points || []}
                    height={360}
                />
            </div>

            <div className="glass-card">
                <h2>DPVI Instability Analysis</h2>
                <div className="metrics-grid">
                    <div>
                        <p className="muted-label">DPVI Score</p>
                        <h3>{patient.dpvi_metrics?.dpvi_score ?? "N/A"}</h3>
                    </div>

                    <div>
                        <p className="muted-label">Available DPVI Features</p>
                        <h3>{patient.dpvi_metrics?.available_dpvi_features ?? 0}</h3>
                    </div>

                    <div>
                        <p className="muted-label">Trend Summary</p>
                        <p>{patient.trend_summary}</p>
                    </div>
                </div>
            </div>

            <div className="glass-card">
                <h2>Multi-Feature Longitudinal Progression</h2>
                <p className="muted-text">
                    All 31 features are plotted across the union of visits.
                    Missing values are left blank and are not interpolated.
                </p>

                <MultiFeatureGraph
                    graphData={patient.multi_feature_graph}
                />
            </div>

            <div className="glass-card">
                <h2>Visit-Wise Clinical Data</h2>
                <div className="table-scroll">
                    <table className="data-table">
                        <thead>
                            <tr>
                                {patient.visit_table?.[0] &&
                                    Object.keys(patient.visit_table[0]).map((key) => (
                                        <th key={key}>{key}</th>
                                    ))}
                            </tr>
                        </thead>

                        <tbody>
                            {patient.visit_table?.map((row, index) => (
                                <tr key={index}>
                                    {Object.values(row).map((value, idx) => (
                                        <td key={idx}>
                                            {value ?? "-"}
                                        </td>
                                    ))}
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            <div className="glass-card">
                <h2>Patient-Level Interpretation</h2>

                <div className="detail-info-grid">

                    <div className="detail-info-card">
                        <p className="muted-label">
                            Correlation of DPVI, Baseline and Actual Status
                        </p>
                        <p>
                            {patient.patient_interpretation?.correlation_of_status ?? "N/A"}
                        </p>
                    </div>

                    <div className="detail-info-card">
                        <p className="muted-label">
                            Clinical Interpretation
                        </p>
                        <p>
                            {patient.patient_interpretation?.clinical_interpretation ?? "N/A"}
                        </p>
                    </div>

                    <div className="detail-info-card">
                        <p className="muted-label">
                            DPVI Contribution
                        </p>
                        <p>
                            {patient.patient_interpretation?.dpvi_contribution ?? "N/A"}
                        </p>
                    </div>

                    <div className="detail-info-card">
                        <p className="muted-label">
                            Prediction Insights
                        </p>
                        <p>
                            {patient.patient_interpretation?.prediction_insights ?? "N/A"}
                        </p>
                    </div>

                    <div className="detail-info-card">
                        <p className="muted-label">
                            Explainability Insights
                        </p>
                        <p>
                            {patient.patient_interpretation?.explainability_insights ?? "N/A"}
                        </p>
                    </div>

                    <div className="detail-info-card">
                        <p className="muted-label">
                            Ablation Analysis
                        </p>
                        <p>
                            {patient.patient_interpretation?.ablation_analysis ?? "N/A"}
                        </p>
                    </div>

                </div>
            </div>

            <div className="glass-card">
                <h2>Best Model Threshold Reference</h2>

                <div className="detail-info-grid">

                    <div className="detail-info-card">
                        <p className="muted-label">Best Model</p>
                        <h3>
                            {patient.winner_model_context?.winner_model ?? "N/A"}
                        </h3>
                    </div>

                    <div className="detail-info-card">
                        <p className="muted-label">Selected Pipeline</p>
                        <h3>
                            {patient.winner_model_context?.selected_pipeline ?? "N/A"}
                        </h3>
                    </div>

                    <div className="detail-info-card">
                        <p className="muted-label">
                            Classification Threshold
                        </p>

                        <h3>
                            {patient.winner_model_context?.model_probability_threshold ?? "N/A"}
                        </h3>
                    </div>

                </div>

                <p className="muted-text">
                    The threshold values below are learned split cutoffs extracted from
                    the selected best model for its most important features.
                </p>

                <div className="table-scroll">
                    <table className="data-table">
                        <thead>
                            <tr>
                                <th>Feature</th>
                                <th>Patient Value</th>
                                <th>Best Model Cutoff</th>
                                <th>Interpretation</th>
                            </tr>
                        </thead>

                        <tbody>
                            {patient.patient_feature_thresholds?.map((row, index) => (
                                <tr key={index}>
                                    <td>{row.feature}</td>

                                    <td>
                                        {row.patient_value ?? "N/A"}
                                    </td>

                                    <td>
                                        {row.threshold_value ?? "N/A"}
                                    </td>

                                    <td>
                                        {row.relation ?? "N/A"}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>



        </div>
    );
}