def add_cols_2019(df):
    if "B05006_099E" in df.columns:
        df["B05006_099E"] = df["B05006_097E"] + df["B05006_098E"] + df["B05006_099E"]
        df.drop(columns=["B05006_097E","B05006_098E"])

    if "B05006_099M" in df.columns:
        df["B05006_099M"] = df["B05006_097M"] + df["B05006_098M"] + df["B05006_099M"]
        df.drop(columns=["B05006_097M","B05006_098M"])

    if "B05006_104E" in df.columns:
        df["B05006_104E"] = df["B05006_102E"] + df["B05006_103E"] + df["B05006_104E"]
        df.drop(columns=["B05006_102E","B05006_103E"])

    if "B05006_104M" in df.columns:
        df["B05006_104M"] = df["B05006_102M"] + df["B05006_103M"] + df["B05006_104M"]
        df.drop(columns=["B05006_102M","B05006_103M"])

    if "B05006_120E" in df.columns:
        df["B05006_120E"] = df["B05006_118E"] + df["B05006_120E"]
        df.drop(columns=["B05006_118E"])

    if "B05006_120M" in df.columns:
        df["B05006_120M"] = df["B05006_118M"] + df["B05006_120M"]
        df.drop(columns=["B05006_118M"])

    if "B05006_128E" in df.columns:
        df["B05006_128E"] = df["B05006_127E"] + df["B05006_128E"]
        df.drop(columns=["B05006_127E"])

    if "B05006_128M" in df.columns:
        df["B05006_128M"] = df["B05006_127M"] + df["B05006_128M"]
        df.drop(columns=["B05006_127M"])

    return df


def change_cols_2019(df, change_dict):
    mapping_dict = {
        "B05006_{}E".format(str(k).zfill(3)): "B05006_{}E".format(str(change_dict[k]).zfill(3)) 
        for k in change_dict.keys()
    }

    df = df.rename(columns=mapping_dict)

    return df