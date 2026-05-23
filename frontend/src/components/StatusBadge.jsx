export default function StatusBadge({ label, type }) {
    const value = label || "Unknown";

    const getClassName = () => {
        if (type === "instability") {
            if (value === "HIGH VOLATILITY") return "badge badge-red";
            if (value === "MODERATE") return "badge badge-yellow";
            if (value === "STABLE") return "badge badge-green";
            return "badge badge-gray";
        }

        if (type === "status") {
            if (value === "Present") return "badge badge-blue";
            if (value === "Absent") return "badge badge-green";
            return "badge badge-gray";
        }

        if (type === "result") {
            if (value === "Correct") return "badge badge-green";
            if (value === "Misclassified") return "badge badge-red";
            return "badge badge-gray";
        }

        return "badge badge-gray";
    };

    return (
        <span className={getClassName()}>
            {value}
        </span>
    );
}