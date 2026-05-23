import {
    Route,
    Routes
} from "react-router-dom";

import Home from "./pages/Home";

import Upload from "./pages/Upload";

import Processing from "./pages/Processing";

import Prediction from "./pages/Prediction";

import Analysis from "./pages/Analysis";

import Navbar from "./components/Navbar";

import GraphResults from "./pages/GraphResults";
import EvaluationLedger from "./pages/EvaluationLedger";

import PatientOverview from "./pages/PatientOverview";
import PatientDetail from "./pages/PatientDetail";

export default function App() {

    return (

        <div className="app-container">

            <Navbar />

            <Routes>

                <Route
                    path="/"
                    element={<Home />}
                />

                <Route
                    path="/upload"
                    element={<Upload />}
                />

                <Route
                    path="/processing"
                    element={<Processing />}
                />

                <Route
                    path="/prediction"
                    element={<Prediction />}
                />

                <Route
                    path="/analysis"
                    element={<Analysis />}
                />

            <Route path="/graphs" element={<GraphResults />} />

            <Route path="/ledger" element={<EvaluationLedger />} />

            <Route path="/patients" element={<PatientOverview />} />
            <Route path="/patients/:patno" element={<PatientDetail />} />

            </Routes>

        </div>
    );
}