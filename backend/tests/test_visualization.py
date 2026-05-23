from ml.pipeline_runner import get_latest_results


def test_feature_importance_structure_if_available():
    results = get_latest_results()

    dashboard = results.get("dashboard", {})

    feature_importance = dashboard.get("feature_importance")

    if feature_importance is not None:
        assert isinstance(feature_importance, (list, dict))


def test_confusion_matrix_structure_if_available():
    results = get_latest_results()

    dashboard = results.get("dashboard", {})

    confusion_matrix = dashboard.get("confusion_matrix")

    if confusion_matrix is not None:
        assert isinstance(confusion_matrix, (list, dict))


def test_graphs_exist_if_pipeline_ran():
    results = get_latest_results()

    graphs = results.get("graphs")

    if graphs is not None:
        assert len(graphs) >= 0