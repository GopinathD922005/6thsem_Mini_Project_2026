import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import Upload from "../pages/Upload";

test("shows error when upload is clicked without selecting file", () => {

    render(
        <MemoryRouter>
            <Upload />
        </MemoryRouter>
    );

    fireEvent.click(
        screen.getByRole("button", {
            name: /Upload & Start Analysis/i
        })
    );

    expect(
        screen.getByText("Please select a ZIP file")
    ).toBeInTheDocument();
});


test("shows error when non zip file is selected", () => {

    render(
        <MemoryRouter>
            <Upload />
        </MemoryRouter>
    );

    const input = document.querySelector("input[type='file']");

    const file = new File(
        ["dummy"],
        "data.txt",
        {
            type: "text/plain"
        }
    );

    fireEvent.change(input, {
        target: {
            files: [file]
        }
    });

    expect(
        screen.getByText("Please upload a ZIP file")
    ).toBeInTheDocument();
});


test("accepts valid zip file selection", () => {

    render(
        <MemoryRouter>
            <Upload />
        </MemoryRouter>
    );

    const input = document.querySelector("input[type='file']");

    const file = new File(
        ["dummy"],
        "data.zip",
        {
            type: "application/zip"
        }
    );

    fireEvent.change(input, {
        target: {
            files: [file]
        }
    });

    expect(input.files[0].name).toBe("data.zip");
});