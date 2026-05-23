import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import Home from "../pages/Home";

test("renders real Home page", () => {
    render(
        <MemoryRouter>
            <Home />
        </MemoryRouter>
    );

    expect(document.body).toBeInTheDocument();
});