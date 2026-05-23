export default function InsightBox({

    title = "Insights",

    insights = []
}) {

    return (

        <div className="insight-box">

            <div className="insight-title">

                {title}

            </div>

            <div className="insight-list">

                {
                    insights.map((item, index) => (

                        <div
                            key={index}
                            className="insight-item"
                        >

                            • {item}

                        </div>
                    ))
                }

            </div>

        </div>
    );
}