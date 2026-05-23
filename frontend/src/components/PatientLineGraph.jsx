import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    Tooltip,
    ResponsiveContainer,
    CartesianGrid,
} from "recharts";

export default function PatientLineGraph({ feature, points, height = 240 }) {
    const data = (points || []).map((point) => ({
        visit: point.visit,
        value: point.value,
    }));

    if (!data.length) {
        return (
            <div className="empty-graph" style={{ height }}>
                No graph data available
            </div>
        );
    }

    return (
        <div className="graph-card" style={{ height }}>
            <p className="graph-title">
                {feature} Progression
            </p>

            <ResponsiveContainer width="100%" height="90%">
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
                        formatter={(value) => [value, feature]}
                        labelFormatter={(label) => `Visit: ${label}`}
                    />

                    <Line
                        type="linear"
                        dataKey="value"
                        name={feature}
                        stroke="#60a5fa"
                        strokeWidth={3}
                        dot={{ r: 4 }}
                        activeDot={{ r: 6 }}
                        connectNulls={false}
                    />
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
}