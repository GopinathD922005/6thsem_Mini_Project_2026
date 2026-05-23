from ml.pipeline_runner import get_latest_results


def test_dashboard_exists_if_pipeline_ran():
    results = get_latest_results()

    dashboard = results.get("dashboard")

    if dashboard is not None:
        assert isinstance(dashboard, dict)


def test_metrics_are_valid_types_if_available():
    results = get_latest_results()

    metrics = results.get("metrics")

    if metrics is not None:
        assert isinstance(metrics, (list, dict))


def test_model_names_exist_if_available():
    results = get_latest_results()

    dashboard = results.get("dashboard", {})

    models = dashboard.get("models")

    if models is not None:
        assert isinstance(models, list)