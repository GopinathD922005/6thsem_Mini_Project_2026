import axios from "axios";


const api = axios.create({

    baseURL: "http://127.0.0.1:8000"
});


/* =====================================================
   UPLOAD ZIP
===================================================== */

export const uploadDataset = async (formData) => {

    const response = await api.post(

        "/upload/",

        formData,

        {
            headers: {
                "Content-Type": "multipart/form-data"
            }
        }
    );

    return response.data;
};


/* =====================================================
   START PIPELINE
===================================================== */

export const startPipeline = async () => {

    const response = await api.post(

        "/run/start"
    );

    return response.data;
};


/* =====================================================
   PIPELINE STATUS
===================================================== */

export const getPipelineStatus = async () => {

    const response = await api.get(

        "/run/status"
    );

    return response.data;
};


/* =====================================================
   PROGRESS LOGS
===================================================== */

export const getProgressLogs = async () => {

    const response = await api.get(

        "/results/progress"
    );

    return response.data;
};


/* =====================================================
   COMPLETE RESULTS
===================================================== */

export const getResults = async () => {

    const response = await api.get(

        "/results/"
    );

    return response.data;
};


/* =====================================================
   SUMMARY
===================================================== */

export const getSummary = async () => {

    const response = await api.get(

        "/results/summary"
    );

    return response.data;
};


/* =====================================================
   METRICS
===================================================== */

export const getMetrics = async () => {

    const response = await api.get(

        "/results/metrics"
    );

    return response.data;
};


/* =====================================================
   FEATURE IMPORTANCE
===================================================== */

export const getFeatureImportance = async () => {

    const response = await api.get(

        "/results/feature-importance"
    );

    return response.data;
};


/* =====================================================
   ABLATION
===================================================== */

export const getAblation = async () => {

    const response = await api.get(

        "/results/ablation"
    );

    return response.data;
};


/* =====================================================
   INSIGHTS
===================================================== */

export const getInsights = async () => {

    const response = await api.get(

        "/results/insights"
    );

    return response.data;
};


/* =====================================================
   CONFUSION MATRIX
===================================================== */

export const getConfusionMatrix = async () => {

    const response = await api.get(

        "/results/confusion-matrix"
    );

    return response.data;
};

export const getGraphResults = async () => {
    const response = await api.get("/results/graphs");
    return response.data;
};

export const getLedgers = async () => {
    const response = await api.get("/results/ledgers");
    return response.data;
};

export const getLatestResults = async () => {
    const response = await api.get("/results/latest");
    return response.data;
};

export const getPatientCards = async () => {
    const response = await api.get("/results/patients");
    return response.data;
};

export const getPatientDetail = async (patno) => {
    const response = await api.get(`/results/patient-detail/${patno}`);
    return response.data;
};

export const getPredictionResults = async () => {
    const response = await api.get("/results/prediction");
    return response.data;
};

export const getAnalysisResults = async () => {
    const response = await api.get("/results/analysis");
    return response.data;
};

export default api;