import "./mocks/apiMock";
import { render } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import Analysis from "../pages/Analysis";


test("renders real Analysis page", () => {
    render(
        <MemoryRouter>
            <Analysis />
        </MemoryRouter>
    );

    expect(document.body).toBeInTheDocument();
});