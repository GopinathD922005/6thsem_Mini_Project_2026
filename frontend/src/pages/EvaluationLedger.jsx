import { useEffect, useState } from "react";

import { motion } from "framer-motion";

import { getLedgers } from "../api";


export default function EvaluationLedger() {

    const [ledgers, setLedgers] = useState({});

    useEffect(() => {
        const fetchData = async () => {
            const response = await getLedgers();

            if (response.success) {
                setLedgers(response.ledgers || {});
            }
        };

        fetchData();
    }, []);

    const ledgerNames = {
        full_train_test: "FINAL ELEVATION REPORT — DPVI Train/Test",
        full_cv: "FINAL CROSS-VALIDATED ELEVATION REPORT — DPVI",
        weighted_train_test: "FINAL ELEVATION REPORT — Weighted DPVI Train/Test",
        weighted_cv: "FINAL CROSS-VALIDATED ELEVATION REPORT — Weighted DPVI"
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
                    <span className="gradient-text">Ledger</span>
                </div>

                <div className="hero-description">
                    Final multimodal elevation reports from all four experiment blocks,
                    displayed as clean dashboard tables instead of backend terminal output.
                </div>

                {Object.keys(ledgerNames).map((key) => {
                    const rows = ledgers[key] || [];

                    const headers = rows.length > 0 ? Object.keys(rows[0]) : [];

                    return (
                        <div key={key} className="ledger-section">
                            <div className="experiment-title">
                                {ledgerNames[key]}
                            </div>

                            {rows.length === 0 ? (
                                <div className="graph-panel">
                                    No ledger data available yet.
                                </div>
                            ) : (
                                <div className="graph-panel" style={{ overflowX: "auto" }}>
                                    <table className="result-table">
                                        <thead>
                                            <tr>
                                                {headers.map((header) => (
                                                    <th key={header}>
                                                        {header}
                                                    </th>
                                                ))}
                                            </tr>
                                        </thead>

                                        <tbody>
                                            {rows.map((row, rowIndex) => (
                                                <tr key={rowIndex}>
                                                    {headers.map((header) => (


<td key={header}>
{
        [
            "Accuracy"
        ].includes(header)

            ? `${(Number(row[header]) * 100).toFixed(2)}%`

            : row[header]
    }
</td>

                                                    ))}
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            )}
                        </div>
                    );
                })}
            </motion.div>
        </div>
    );
}