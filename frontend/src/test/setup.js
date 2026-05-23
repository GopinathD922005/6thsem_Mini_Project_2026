import "@testing-library/jest-dom";

const originalWarn = console.warn;
const originalError = console.error;

beforeAll(() => {

    console.warn = (...args) => {

        const message = args[0];

        if (
            typeof message === "string" &&
            (
                message.includes("React Router Future Flag Warning")
            )
        ) {
            return;
        }

        originalWarn(...args);
    };

    console.error = (...args) => {

        const message = args[0];

        if (
            typeof message === "string" &&
            (
                message.includes("not wrapped in act")
            )
        ) {
            return;
        }

        originalError(...args);
    };
});