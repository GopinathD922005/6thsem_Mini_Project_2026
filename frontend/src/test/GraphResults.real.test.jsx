import "./mocks/apiMock";
import { render } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import GraphResults from "../pages/GraphResults";

test("renders real GraphResults page", () => {
    render(
        <MemoryRouter>
            <GraphResults />
        </MemoryRouter>
    );

    expect(document.body).toBeInTheDocument();
});