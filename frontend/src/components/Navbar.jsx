import {
    Link,
    useLocation
} from "react-router-dom";

import {
    ActivitySquare
} from "lucide-react";


export default function Navbar() {

    const location = useLocation();

    const isActive = (path) => {

        return location.pathname.startsWith(path);
        //return location.pathname === path;
    };

    return (

        <nav className="navbar">

            {/* =========================================
                LOGO
            ========================================= */}

            <div className="logo">

                <ActivitySquare
                    size={26}
                    style={{
                        marginRight: "10px",
                        verticalAlign: "middle"
                    }}
                />

                DPVI System

            </div>


            {/* =========================================
                NAVIGATION LINKS
            ========================================= */}

            <div className="nav-links">

                <Link
                    to="/"
                    className="nav-link"
                    style={{
                        color: isActive("/") ? "#60a5fa" : "white"
                    }}
                >
                    Home
                </Link>

                <Link
                    to="/upload"
                    className="nav-link"
                    style={{
                        color: isActive("/upload") ? "#60a5fa" : "white"
                    }}
                >
                    Upload
                </Link>

                <Link
                    to="/processing"
                    className="nav-link"
                    style={{
                        color: isActive("/processing") ? "#60a5fa" : "white"
                    }}
                >
                    Processing
                </Link>

                <Link
                    to="/prediction"
                    className="nav-link"
                    style={{
                        color: isActive("/prediction") ? "#60a5fa" : "white"
                    }}
                >
                    Prediction
                </Link>

                <Link
                    to="/analysis"
                    className="nav-link"
                    style={{
                        color: isActive("/analysis") ? "#60a5fa" : "white"
                    }}
                >
                    Analysis
                </Link>


<Link
    to="/graphs"
    className="nav-link"
    style={{
        color: isActive("/graphs") ? "#60a5fa" : "white"
    }}
>
    Graphs
</Link>

<Link
    to="/ledger"
    className="nav-link"
    style={{
        color: isActive("/ledger") ? "#60a5fa" : "white"
    }}
>
    Ledger
</Link>


<Link
    to="/patients"
    className="nav-link"
    style={{
        color: isActive("/patients") ? "#60a5fa" : "white"
    }}
>
    Patients
</Link>


            </div>

        </nav>
    );
}