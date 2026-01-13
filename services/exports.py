from __future__ import annotations
import io
import pandas as pd

def df_to_csv_bytes(df: pd.DataFrame) -> bytes:
    if df is None:
        df = pd.DataFrame()

    buf = io.StringIO()
    df.to_csv(buf, index=False)
    return ("\ufeff" + buf.getvalue()).encode("utf-8")
