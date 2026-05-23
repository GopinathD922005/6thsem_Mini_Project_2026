import pandas as pd


def transform_to_event_stream(data_dict, category_label):
    """
    Standardizes diverse CSVs into a 5-column event stream:
    PATNO | EVENT_ID | MEASURE_NAME | MEASURE_VALUE | CATEGORY
    """
    all_events = []

    for file_name, df in data_dict.items():
        df = df.copy()

        # 1. Robust patient ID resolver
        id_mapper = {
            col.upper().replace(" ", "").replace("_", "").replace("-", ""): col
            for col in df.columns
        }

        if "PATNO" in id_mapper:
            df = df.rename(columns={id_mapper["PATNO"]: "PATNO"})
        elif "ALIASID" in id_mapper:
            df = df.rename(columns={id_mapper["ALIASID"]: "PATNO"})
        elif "SUBJECTID" in id_mapper:
            df = df.rename(columns={id_mapper["SUBJECTID"]: "PATNO"})
        elif "SUBID" in id_mapper:
            df = df.rename(columns={id_mapper["SUBID"]: "PATNO"})
        else:
            #print(f"⚠️ Skipping {file_name}: No Patient ID (PATNO/SUBJECTID) found.")
            pass

        # 2. Standardize visit ID
        visit_col = None
        for col in ["EVENT_ID", "VISNO", "VISIT_ID", "CLINICAL_EVENT", "VISIT", "VISITNAME"]:
            clean_col = col.upper().replace("_", "")
            if clean_col in id_mapper:
                visit_col = id_mapper[clean_col]
                break

        if visit_col:
            df = df.rename(columns={visit_col: "EVENT_ID"})
        else:
            df["EVENT_ID"] = "BL"

        # 3. Data extraction
        exclude = [
            "PATNO", "EVENT_ID", "REC_ID", "INFODT", "ORIG_ENTRY",
            "LAST_UPDATE", "STARTTIME", "STOPTIME", "RUNDATE", "QRSDTM",
        ]

        value_vars = [
            c for c in df.select_dtypes(include=["number"]).columns
            if c.upper().replace("_", "") not in exclude
        ]

        if not value_vars:
            continue

        try:
            long_df = pd.melt(
                df,
                id_vars=["PATNO", "EVENT_ID"],
                value_vars=value_vars,
                var_name="MEASURE_NAME",
                value_name="MEASURE_VALUE",
            )
            long_df["CATEGORY"] = category_label
            all_events.append(long_df)
        except Exception as e:
            #print(f"⚠️ Skipping {file_name} due to structure error: {e}")
            pass

    return pd.concat(all_events, axis=0) if all_events else pd.DataFrame(
        columns=["PATNO", "EVENT_ID", "MEASURE_NAME", "MEASURE_VALUE", "CATEGORY"]
    )
