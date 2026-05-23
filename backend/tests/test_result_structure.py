from ml.pipeline_runner import get_latest_results


def test_graph_results_structure_if_available():
    results = get_latest_results()

    graphs = results.get("graphs")

    if graphs is not None:
        assert isinstance(graphs, (dict, list))


def test_metrics_structure_if_available():
    results = get_latest_results()

    metrics = results.get("metrics")

    if metrics is not None:
        assert isinstance(metrics, (dict, list))


def test_ledger_structure_if_available():
    results = get_latest_results()

    ledger = results.get("ledger")

    if ledger is not None:
        assert isinstance(ledger, (dict, list))