export default function PatientFilters({ filters, setFilters }) {
    const updateFilter = (key, value) => {
        setFilters((prev) => ({
            ...prev,
            [key]: value,
        }));
    };

    return (
        <div className="glass-card patient-filters">
            <input
                type="text"
                placeholder="Search Patient ID"
                value={filters.search}
                onChange={(e) => updateFilter("search", e.target.value)}
                className="filter-input"
            />

            <select
                value={filters.actualStatus}
                onChange={(e) => updateFilter("actualStatus", e.target.value)}
                className="filter-input"
            >
                <option>All</option>
                <option>Present</option>
                <option>Absent</option>
                <option>Unknown</option>
            </select>

            <select
                value={filters.dpviPredictedStatus}
                onChange={(e) => updateFilter("dpviPredictedStatus", e.target.value)}
                className="filter-input"
            >
                <option>All</option>
                <option>Present</option>
                <option>Absent</option>
                <option>Unknown</option>
            </select>

            <select
                value={filters.baselinePredictedStatus}
                onChange={(e) => updateFilter("baselinePredictedStatus", e.target.value)}
                className="filter-input"
            >
                <option>All</option>
                <option>Present</option>
                <option>Absent</option>
                <option>Unknown</option>
            </select>

            <select
                value={filters.dpviPredictionResult}
                onChange={(e) => updateFilter("dpviPredictionResult", e.target.value)}
                className="filter-input"
            >
                <option>All</option>
                <option>Correct</option>
                <option>Misclassified</option>
                <option>Unknown</option>
            </select>

            <select
                value={filters.baselinePredictionResult}
                onChange={(e) => updateFilter("baselinePredictionResult", e.target.value)}
                className="filter-input"
            >
                <option>All</option>
                <option>Correct</option>
                <option>Misclassified</option>
                <option>Unknown</option>
            </select>

            <select
                value={filters.instability}
                onChange={(e) => updateFilter("instability", e.target.value)}
                className="filter-input"
            >
                <option>All</option>
                <option>STABLE</option>
                <option>MODERATE</option>
                <option>HIGH VOLATILITY</option>
                <option>Unavailable</option>
            </select>

            <input
                type="number"
                min="0"
                max="1"
                step="0.01"
                placeholder="Min DPVI"
                value={filters.minDpvi}
                onChange={(e) => updateFilter("minDpvi", e.target.value)}
                className="filter-input"
            />

            <input
                type="number"
                min="0"
                max="1"
                step="0.01"
                placeholder="Max DPVI"
                value={filters.maxDpvi}
                onChange={(e) => updateFilter("maxDpvi", e.target.value)}
                className="filter-input"
            />

            <select
                value={filters.sortBy}
                onChange={(e) => updateFilter("sortBy", e.target.value)}
                className="filter-input"
            >
                <option>Highest DPVI</option>
                <option>Lowest DPVI</option>
                <option>Most Visits</option>
                <option>Patient ID</option>
            </select>
        </div>
    );
}