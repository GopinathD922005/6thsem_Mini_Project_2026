export default function ProgressTimeline({

    logs = []
}) {

    return (

        <div className="progress-list">

            {
                logs.length === 0 ? (

                    <div className="progress-item">

                        Waiting for processing to start...

                    </div>

                ) : (

                    logs.map((log, index) => (

                        <div
                            key={index}
                            className="progress-item"
                        >

                            <strong>

                                [{log.time}]

                            </strong>

                            {" "}

                            {log.message}

                        </div>
                    ))
                )
            }

        </div>
    );
}