import "./mocks/apiMock"
import { render } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import PatientOverview from "../pages/PatientOverview";

test("renders real PatientOverview page", () => {
    render(
        <MemoryRouter>
            <PatientOverview />
        </MemoryRouter>
    );

    expect(document.body).toBeInTheDocument();
});