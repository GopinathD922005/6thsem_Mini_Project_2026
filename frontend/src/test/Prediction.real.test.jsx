import "./mocks/apiMock";
import { render } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import Prediction from "../pages/Prediction";

test("renders real Prediction page", () => {
    render(
        <MemoryRouter>
            <Prediction />
        </MemoryRouter>
    );

    expect(document.body).toBeInTheDocument();
});