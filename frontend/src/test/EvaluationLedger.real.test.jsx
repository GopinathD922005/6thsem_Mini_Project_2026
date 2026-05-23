import "./mocks/apiMock";
import { render } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import EvaluationLedger from "../pages/EvaluationLedger";

test("renders real EvaluationLedger page", () => {
    render(
        <MemoryRouter>
            <EvaluationLedger />
        </MemoryRouter>
    );

    expect(document.body).toBeInTheDocument();
});