import { vi } from "vitest";

vi.mock("../../api", () => ({

    getResults: vi.fn(() =>
        Promise.resolve({
            success: true,
            data: {}
        })
    ),

    getGraphResults: vi.fn(() =>
        Promise.resolve({
            success: true,
            graphs: []
        })
    ),

    getLedgers: vi.fn(() =>
        Promise.resolve({
            success: true,
            ledgers: []
        })
    ),

    getPatients: vi.fn(() =>
        Promise.resolve({
            success: true,
            patients: []
        })
    ),

    getPatientCards: vi.fn(() =>
        Promise.resolve({
            success: true,
            patients: []
        })
    ),

    getProgressLogs: vi.fn(() =>
        Promise.resolve({
            success: true,
            progress: []
        })
    ),

    getPipelineStatus: vi.fn(() =>
        Promise.resolve({
            running: false
        })
    ),

    getPredictionResults: vi.fn(() =>
        Promise.resolve({
            success: true,
            results: {},
            prediction: {}
        })
    ),

    getAnalysisResults: vi.fn(() =>
        Promise.resolve({
            success: true,
            analysis: {
                metrics: {},
                ablation: {},
                explainability_insights: [],
                feature_importance: [],
                confusion_matrix: {}
            }
        })
    )

}));