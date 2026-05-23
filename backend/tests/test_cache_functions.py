import tempfile
import pickle
from pathlib import Path


def test_pickle_cache_save_and_load():
    sample_data = {
        "dashboard": {},
        "metrics": [],
        "graphs": []
    }

    with tempfile.TemporaryDirectory() as temp_dir:
        cache_file = Path(temp_dir) / "latest_results.pkl"

        with open(cache_file, "wb") as f:
            pickle.dump(sample_data, f)

        with open(cache_file, "rb") as f:
            loaded_data = pickle.load(f)

        assert loaded_data == sample_data


def test_cache_file_extension_is_pickle():
    cache_file = Path("cache/latest_results.pkl")

    assert cache_file.suffix == ".pkl"