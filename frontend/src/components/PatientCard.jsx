import PatientLineGraph from "./PatientLineGraph";
import StatusBadge from "./StatusBadge";

export default function PatientCard({ patient, onViewDetails }) {
    return (
        <div className="glass-card patient-card">
            <div className="patient-card-header">
                <div>
                    <p className="muted-label">PATNO</p>
                    <h2>{patient.patno}</h2>
                </div>

                <StatusBadge label={patient.instability} type="instability" />
            </div>

            <div className="patient-status-grid">
                <div>
                    <p className="muted-label">Actual Disease Status</p>
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
            </div>

            <div className="dpvi-row">
                <div>
                    <p className="muted-label">DPVI Score</p>
                    <h3>{patient.dpvi_score ?? "N/A"}</h3>
                </div>

                <div>
                    <p className="muted-label">Primary Volatility Feature</p>
                    <h3>{patient.primary_volatility_feature}</h3>
                </div>
            </div>

            <PatientLineGraph
                feature={patient.brief_graph?.feature}
                points={patient.brief_graph?.points || []}
                height={210}
            />

            <div className="trend-box">
                <p className="muted-label">Trend Summary</p>
                <p>{patient.trend_summary}</p>
            </div>

            <div className="patient-card-footer">
                <span>{patient.visit_count} longitudinal visits available</span>

                <button
                    className="primary-button"
                    onClick={onViewDetails}
                >
                    View Details
                </button>
            </div>
        </div>
    );
}