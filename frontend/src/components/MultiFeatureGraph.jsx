import { useMemo, useState } from "react";
import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    Tooltip,
    ResponsiveContainer,
    CartesianGrid,
    Legend,
} from "recharts";

const COLORS = [
    "#60a5fa", "#a78bfa", "#34d399", "#fbbf24", "#fb7185",
    "#22d3ee", "#f472b6", "#c084fc", "#4ade80", "#f97316",
    "#38bdf8", "#e879f9", "#2dd4bf", "#fde047", "#818cf8",
];

export default function MultiFeatureGraph({ graphData }) {
    const [visibleFeatures, setVisibleFeatures] = useState({});

    const features = Object.keys(graphData?.feature_series || {});

    const data = useMemo(() => {
        if (!graphData?.union_visits) return [];

        return graphData.union_visits.map((visit, index) => {
            const row = { visit };

            features.forEach((feature) => {
                row[feature] =
                    graphData.feature_series[feature]?.[index]?.value ?? null;
            });

            return row;
        });
    }, [graphData, features]);

    const activeFeatures = features.filter((feature) => {
        if (Object.keys(visibleFeatures).length === 0) {
            return true;
        }

        return visibleFeatures[feature] !== false;
    });

    const toggleFeature = (feature) => {
        setVisibleFeatures((prev) => ({
            ...prev,
            [feature]: prev[feature] === false,
        }));
    };

    if (!data.length) {
        return (
            <div className="empty-graph" style={{ height: 360 }}>
                No multi-feature graph data available
            </div>
        );
    }

    return (
        <div>
            <div className="feature-selector">
                {features.map((feature) => (
                    <button
                        key={feature}
                        className={
                            activeFeatures.includes(feature)
                                ? "feature-chip active"
                                : "feature-chip"
                        }
                        onClick={() => toggleFeature(feature)}
                    >
                        {feature}
                    </button>
                ))}
            </div>

            <div className="graph-card large-graph">
                <ResponsiveContainer width="100%" height={460}>
                    <LineChart data={data}>
                        <CartesianGrid strokeDasharray="3 3" opacity={0.2} />

                        <XAxis
                            dataKey="visit"
                            tick={{ fill: "#cbd5e1", fontSize: 11 }}
                        />

                        <YAxis
                            tick={{ fill: "#cbd5e1", fontSize: 11 }}
                        />

                        <Tooltip
                            contentStyle={{
                                background: "#0f172a",
                                border: "1px solid rgba(148,163,184,0.3)",
                                borderRadius: "12px",
                                color: "white",
                            }}
                            labelFormatter={(label) => `Visit: ${label}`}
                        />

                        <Legend />

                        {activeFeatures.map((feature, index) => (
                            <Line
                                key={feature}
                                type="linear"
                                dataKey={feature}
                                name={feature}
                                stroke={COLORS[index % COLORS.length]}
                                strokeWidth={2}
                                dot={{ r: 3 }}
                                activeDot={{ r: 6 }}
                                connectNulls={false}
                            />
                        ))}
                    </LineChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
}