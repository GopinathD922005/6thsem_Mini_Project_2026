from ml.pipeline_runner import get_latest_results


def test_latest_results_returns_dictionary():
    results = get_latest_results()

    assert isinstance(results, dict)


def test_latest_results_has_expected_basic_structure():
    results = get_latest_results()

    assert results is not None
    assert isinstance(results, dict)


def test_latest_results_contains_expected_keys_if_pipeline_ran():
    results = get_latest_results()

    if results:

        expected_keys = [
            "dashboard",
            "patient_visualization"
        ]

        for key in expected_keys:
            assert key in results


def test_dashboard_structure_if_available():
    results = get_latest_results()

    dashboard = results.get("dashboard")

    if dashboard is not None:
        assert isinstance(dashboard, dict)