def print_dataset_info(dataset_dict, name):
    print(f"\n{name.upper()} DATASETS ({len(dataset_dict)} files):")
    print("-" * 50)

    total_rows = 0
    for file_name, df in dataset_dict.items():
        rows = df.shape[0]
        total_rows += rows
        print(f"{file_name}: {rows} samples")

    print("-" * 50)
    print(f"TOTAL samples in {name}: {total_rows}\n")


def print_dataset_preview(dataset_dict, name):
    print("\n" + "=" * 60)
    print(f"🚀 {name.upper()} DATASET PREVIEW")
    print("=" * 60)

    if dataset_dict:
        file_name = list(dataset_dict.keys())[0]
        df = dataset_dict[file_name]

        print(f"📄 Printing the first file: {file_name}")
        print(f"📊 Total Rows in file: {len(df)} samples")
        print(f"📑 Total Columns in file: {len(df.columns)}")
        print("-" * 50)
        print("🔍 Data (First 5 rows):")
        print(df.head())
        print("-" * 60)
    else:
        print(f"⚠️ No files found in the {name} dictionary.")


def print_structured_columns(df):
    cols = list(df.columns)

    id_cols = ["PATNO"]
    base_cols = [c for c in cols if c.startswith("BASE_")]
    dpvi_cols = [c for c in cols if c.startswith("DPVI_")]

    print("\n" + "=" * 60)
    print("📊 FINAL ML FEATURE MATRIX: STRUCTURED OVERVIEW")
    print("=" * 60)

    print(f"\n🆔 PRIMARY IDENTIFIER ({len(id_cols)} column):")
    print(f" → {id_cols}")

    print(f"\n📌 BASELINE FEATURES ({len(base_cols)} columns):")
    print(" (Represents the average severity/state of the patient)")
    print(f" Samples: {base_cols[:5]} ... [+ {max(len(base_cols)-5, 0)} more]")

    print(f"\n🧠 DPVI VARIABILITY FEATURES ({len(dpvi_cols)} columns):")
    print(" (5 components per feature: std, prog_rate, spikes, reversals, entropy)")

    unique_features = []
    for c in dpvi_cols:
        clean_name = c.replace("DPVI_", "")
        for suffix in ["_std", "_prog_rate", "_spikes", "_reversals", "_entropy"]:
            if clean_name.endswith(suffix):
                clean_name = clean_name[: -len(suffix)]
                break
        unique_features.append(clean_name)
    unique_features = sorted(set(unique_features))

    print(f" Calculated for {len(unique_features)} unique biological signals:")

    motor = [f for f in unique_features if "NP3" in f or "NP2" in f]
    digital = [f for f in unique_features if f not in motor and "NP1" not in f and "MCA" not in f]
    other = [f for f in unique_features if f not in motor and f not in digital]

    print(f" • Motor (UPDRS): {motor}")
    print(f" • Digital (Gait): {digital[:4]} ...")
    print(f" • Cognitive/Non-Motor: {other}")
    print("\n" + "=" * 60)
    print(f"✅ TOTAL COLUMNS: {len(cols)} | TOTAL PATIENTS: {len(df)}")
    print("=" * 60)


def print_structured_train_ready_columns(df):
    cols = list(df.columns)
    id_cols = ["PATNO"]

    base_cols = [
        c for c in cols
        if (c.endswith("_last") or c.startswith("BASE_")) and c not in id_cols
    ]

    dpvi_suffixes = ["_std", "_prog_rate", "_spikes", "_reversals", "_entropy"]
    dpvi_cols = [c for c in cols if c.startswith("DPVI_")]

    target_cols = [c for c in cols if c not in id_cols and c not in base_cols and c not in dpvi_cols]

    print("\n" + "=" * 80)
    print("📊 TRAIN-READY DATAFRAME: ARCHITECTURAL OVERVIEW")
    print("=" * 80)

    print(f"\n🆔 PRIMARY IDENTIFIER: {id_cols}")

    print(f"\n📌 BASELINE FEATURES ({len(base_cols)} columns):")
    print(" (Static clinical snapshots - System A)")
    if base_cols:
        print(f" Samples: {base_cols[:4]} ...")

    print(f"\n🧠 DPVI VOLATILITY FEATURES ({len(dpvi_cols)} columns):")
    print(" (The 5 volatility pillars - System B)")

    unique_signals_list = []
    for c in dpvi_cols:
        clean_name = c.replace("DPVI_", "")
        for suffix in dpvi_suffixes:
            if clean_name.endswith(suffix):
                clean_name = clean_name[: -len(suffix)]
                break
        unique_signals_list.append(clean_name)

    unique_signals_count = len(set(unique_signals_list))
    print(f" Total: {len(dpvi_cols)} features (Calculated for {unique_signals_count} unique signals)")
    print(" Pillars per signal: 5 (Std, Prog, Spikes, Rev, Entropy)")
    if dpvi_cols:
        print(f" Samples: {dpvi_cols[:5]} ...")

    print(f"\n🎯 TARGET LABELS / PREDICTION GOALS ({len(target_cols)} columns):")
    print(f" → {target_cols}")

    print("\n" + "=" * 80)
    print(f"✅ FINAL DIMENSIONS: {len(df):,} Patients x {len(cols)} Columns")
    print("=" * 80)

    print("\n📜 FULL LIST OF ALL COLUMN NAMES:")
    print("-" * 40)
    for i, col_name in enumerate(cols, 1):
        print(f"{i:03}. {col_name}")
    print("-" * 40)


def print_structured_weighted_columns(df):
    cols = list(df.columns)

    id_cols = ["PATNO"]
    target_cols = ["FINAL_STATUS"]
    base_cols = [c for c in cols if c.startswith("BASE_")]
    dpvi_cols = [c for c in cols if c.startswith("DPVI_")]

    print("\n" + "=" * 80)
    print("📊 WEIGHTED TRAIN-READY DATAFRAME: ARCHITECTURAL OVERVIEW")
    print("=" * 80)

    print(f"\n🆔 PRIMARY IDENTIFIER: {id_cols}")

    print(f"\n📌 BASELINE SNAPSHOTS ({len(base_cols)} columns):")
    print(" (The initial clinical state of the patient - System A)")
    if base_cols:
        print(f" Samples: {base_cols[:3]} ... {base_cols[-1]}")

    print(f"\n🧠 FUSED DPVI VOLATILITY ({len(dpvi_cols)} columns):")
    print(" (Weighted Fusion: 0.3*Ent + 0.25*Rev + 0.15*Spk + 0.2*Prog + 0.1*Std)")
    print(f" Total: {len(dpvi_cols)} features (One combined index per clinical signal)")
    if dpvi_cols:
        print(f" Samples: {dpvi_cols[:3]} ... {dpvi_cols[-1]}")

    print("\n🎯 TARGET LABELS / PREDICTION GOAL:")
    print(f" → {target_cols} (The progression outcome to be predicted)")

    print("\n" + "=" * 80)
    print(f"✅ FINAL DIMENSIONS: {len(df):,} Patients x {len(cols)} Columns")
    print("=" * 80)

    print("\n📜 FULL LIST OF ALL WEIGHTED COLUMN NAMES:")
    print("-" * 50)
    for i, col_name in enumerate(cols, 1):
        tag = ""
        if col_name in base_cols:
            tag = "[BASELINE]"
        elif col_name in dpvi_cols:
            tag = "[DPVI-FUSED]"
        elif col_name in target_cols:
            tag = "[TARGET]"
        print(f"{i:03}. {col_name:<30} {tag}")
    print("-" * 50)
