import "./mocks/apiMock";
import { render } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import Processing from "../pages/Processing";


test("renders real Processing page", () => {
    render(
        <MemoryRouter>
            <Processing />
        </MemoryRouter>
    );

    expect(document.body).toBeInTheDocument();
});