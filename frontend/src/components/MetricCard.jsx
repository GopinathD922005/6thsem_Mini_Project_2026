export default function MetricCard({

    title,

    value,

    suffix = ""
}) {

    return (

        <div className="metric-card">

            <div className="metric-title">

                {title}

            </div>

            <div className="metric-value">

                {value}

                {suffix}

            </div>

        </div>
    );
}