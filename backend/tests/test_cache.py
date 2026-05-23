from pathlib import Path


def test_cache_folder_exists_or_can_be_created():
    cache_dir = Path("cache")
    cache_dir.mkdir(exist_ok=True)

    assert cache_dir.exists()
    assert cache_dir.is_dir()


def test_cache_file_path_is_valid():
    cache_file = Path("cache/latest_results.pkl")

    assert cache_file.parent.name == "cache"
    assert cache_file.name == "latest_results.pkl"