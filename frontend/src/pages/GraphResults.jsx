import { useEffect, useState } from "react";

import { motion } from "framer-motion";

import { getGraphResults } from "../api";

import ChartCard from "../components/ChartCard";


export default function GraphResults() {

    const [graphs, setGraphs] = useState({});

    useEffect(() => {

        const fetchData = async () => {

            const response = await getGraphResults();

            if (response.success) {

                setGraphs(response.graphs || {});
            }
        };

        fetchData();

    }, []);


    const experimentNames = {
        full_train_test: " DPVI Train/Test Graphs",
        full_cv: " DPVI Cross-Validation Graphs",
        weighted_train_test: "Weighted DPVI Train/Test Graphs",
        weighted_cv: "Weighted DPVI Cross-Validation Graphs"
    };


    return (

        <div className="page-container">

            <motion.div
                className="glass-card"
                initial={{ opacity: 0, y: 35 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.7 }}
            >

                <div className="hero-title">

                    Evaluation
                    <br />

                    <span className="gradient-text">

                        Backend Graphs

                    </span>

                </div>


                <div className="hero-description">

                    This page displays the same backend-generated
                    Matplotlib and Seaborn graphs from the original
                    evaluation code: confusion matrix on the left,
                    ROC curve in the middle, accuracy vs epochs on the right,
                    and model accuracy percentage below the graph.

                </div>


                {
                    Object.keys(experimentNames).map((key) => {

                        const items = graphs[key] || [];

                        return (

                            <div
                                key={key}
                                className="experiment-section"
                            >

                                <div className="experiment-title">

                                    {experimentNames[key]}

                                </div>


                                {
                                    items.length === 0 ? (

                                        <div className="graph-panel">

                                            No backend graph data available yet.

                                        </div>

                                    ) : (

                                        <div className="chart-grid">

                                            {
                                                items.map((item, index) => (

                                                    <ChartCard
                                                        key={index}
                                                        title={`${item.model} — ${item.approach}`}
                                                    >

                                                        {
                                                            item.image ? (

                                                                <>

                                                                    <img
                                                                        src={`data:image/png;base64,${item.image}`}
                                                                        alt={`${item.model} ${item.approach}`}
                                                                        className="backend-graph-image"
                                                                    />

                                                                    <div className="model-accuracy-badge">

                                                                        MODEL ACCURACY: {item.accuracy_percent}

                                                                    </div>

                                                                </>

                                                            ) : (

                                                                <div className="graph-panel">

                                                                    Graph image not available.

                                                                </div>
                                                            )
                                                        }

                                                    </ChartCard>
                                                ))
                                            }

                                        </div>
                                    )
                                }

                            </div>
                        );
                    })
                }

            </motion.div>

        </div>
    );
}