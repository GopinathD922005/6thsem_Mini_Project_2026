import pandas as pd


def test_empty_dataframe_detection():
    df = pd.DataFrame()

    assert df.empty is True


def test_dataframe_columns_validation():
    df = pd.DataFrame({
        "PATNO": [1, 2],
        "EVENT_ID": ["BL", "V01"]
    })

    required_columns = ["PATNO", "EVENT_ID"]

    for column in required_columns:
        assert column in df.columns


def test_dataframe_row_count():
    df = pd.DataFrame({
        "PATNO": [1, 2, 3]
    })

    assert len(df) == 3