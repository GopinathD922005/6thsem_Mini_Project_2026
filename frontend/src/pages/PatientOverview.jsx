import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getPatientCards } from "../api";
import PatientCard from "../components/PatientCard";
import PatientFilters from "../components/PatientFilters";

export default function PatientOverview() {
    const navigate = useNavigate();

    const [patients, setPatients] = useState([]);
    const [loading, setLoading] = useState(true);

    const [filters, setFilters] = useState({
        search: "",
        actualStatus: "All",

        dpviPredictedStatus: "All",
        baselinePredictedStatus: "All",

        dpviPredictionResult: "All",
        baselinePredictionResult: "All",
        instability: "All",
        minDpvi: "",
        maxDpvi: "",
        sortBy: "Highest DPVI",
    });

    useEffect(() => {
        const loadPatients = async () => {
            try {
                const data = await getPatientCards();
                setPatients(data.patients || []);
            } catch (error) {
                console.error("Failed to load patients", error);
            } finally {
                setLoading(false);
            }
        };

        loadPatients();
    }, []);

    const filteredPatients = useMemo(() => {
        let result = [...patients];

        if (filters.search.trim()) {
            result = result.filter((p) =>
                String(p.patno).includes(filters.search.trim())
            );
        }

        if (filters.actualStatus !== "All") {
            result = result.filter((p) => p.actual_status === filters.actualStatus);
        }

        if (filters.dpviPredictedStatus !== "All") {
            result = result.filter(
                (p) => p.dpvi_predicted_status === filters.dpviPredictedStatus
            );
        }

        if (filters.baselinePredictedStatus !== "All") {
            result = result.filter(
                (p) => p.baseline_predicted_status === filters.baselinePredictedStatus
            );
        }

        if (filters.dpviPredictionResult !== "All") {
            result = result.filter(
                (p) => p.dpvi_prediction_result === filters.dpviPredictionResult
            );
        }

        if (filters.baselinePredictionResult !== "All") {
            result = result.filter(
                (p) => p.baseline_prediction_result === filters.baselinePredictionResult
            );
        }

        if (filters.instability !== "All") {
            result = result.filter((p) => p.instability === filters.instability);
        }

        if (filters.minDpvi !== "") {
            result = result.filter((p) => Number(p.dpvi_score) >= Number(filters.minDpvi));
        }

        if (filters.maxDpvi !== "") {
            result = result.filter((p) => Number(p.dpvi_score) <= Number(filters.maxDpvi));
        }

        result.sort((a, b) => {
            if (filters.sortBy === "Highest DPVI") {
                return Number(b.dpvi_score || 0) - Number(a.dpvi_score || 0);
            }

            if (filters.sortBy === "Lowest DPVI") {
                return Number(a.dpvi_score || 0) - Number(b.dpvi_score || 0);
            }

            if (filters.sortBy === "Most Visits") {
                return Number(b.visit_count || 0) - Number(a.visit_count || 0);
            }

            return String(a.patno).localeCompare(String(b.patno));
        });

        return result;
    }, [patients, filters]);

    const visiblePatients = filteredPatients.slice(0, 25);

    if (loading) {
        return (
            <div className="page-shell">
                <div className="glass-card">
                    Loading patient progression dashboard...
                </div>
            </div>
        );
    }

    return (
        <div className="page-shell">
            <div className="page-header">
                <h1>Patient Progression Overview</h1>
                <p>Disease progression volatility summary for trained patients.</p>
            </div>

            <PatientFilters filters={filters} setFilters={setFilters} />

            <p className="muted-text">
                Showing {visiblePatients.length} of {filteredPatients.length} patients.
                Use search/filter to narrow results.
            </p>

            <div className="patient-grid">
                {visiblePatients.map((patient) => (
                    <PatientCard
                        key={patient.patno}
                        patient={patient}
                        onViewDetails={() => navigate(`/patients/${patient.patno}`)}
                    />
                ))}
            </div>
        </div>
    );
}