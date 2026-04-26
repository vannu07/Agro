import argparse
import os
import re
from datetime import datetime

import pandas as pd
import requests


DEFAULT_OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Data-processed", "market_trend.csv")


def normalize_market_df(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()

    normalized = {}
    for col in df.columns:
        key = re.sub(r"[^a-z0-9]", "", str(col).strip().lower())
        normalized[key] = col

    def pick(*aliases):
        for alias in aliases:
            if alias in normalized:
                return normalized[alias]
        return None

    col_map = {
        "state": pick("state"),
        "district": pick("district"),
        "market": pick("market", "marketname"),
        "commodity": pick("commodity", "crop"),
        "variety": pick("variety"),
        "arrival_date": pick("arrivaldate"),
        "min_price": pick("minprice", "minimumprice"),
        "max_price": pick("maxprice", "maximumprice"),
        "modal_price": pick("modalprice"),
    }

    out = pd.DataFrame()
    for target_col, src_col in col_map.items():
        out[target_col] = df[src_col] if src_col in df.columns else ""

    for col in ["state", "district", "market", "commodity", "variety", "arrival_date"]:
        out[col] = out[col].astype(str).str.strip()

    for col in ["min_price", "max_price", "modal_price"]:
        out[col] = pd.to_numeric(out[col], errors="coerce")

    out = out.dropna(subset=["modal_price"], how="all")
    out = out[out["arrival_date"].astype(str).str.len() > 0]
    out = out.drop_duplicates(
        subset=["state", "district", "market", "commodity", "variety", "arrival_date", "modal_price"]
    )

    return out


def fetch_all_records(resource_id: str, api_key: str, limit: int, max_pages: int) -> pd.DataFrame:
    base_url = f"https://api.data.gov.in/resource/{resource_id}"
    all_records = []

    for page in range(max_pages):
        offset = page * limit
        params = {
            "api-key": api_key,
            "format": "json",
            "offset": offset,
            "limit": limit,
        }
        resp = requests.get(base_url, params=params, timeout=20)
        resp.raise_for_status()
        payload = resp.json() if resp.content else {}
        records = payload.get("records", [])
        if not records:
            break

        all_records.extend(records)
        print(f"Fetched page={page + 1}, records={len(records)}, total={len(all_records)}")

        if len(records) < limit:
            break

    return pd.DataFrame(all_records)


def main():
    parser = argparse.ArgumentParser(description="Sync market trends CSV from data.gov.in API")
    parser.add_argument("--resource-id", default=os.getenv("MARKET_API_RESOURCE_ID", ""), help="data.gov.in resource id")
    parser.add_argument("--api-key", default=os.getenv("MARKET_API_KEY", ""), help="data.gov.in api key")
    parser.add_argument("--limit", type=int, default=int(os.getenv("MARKET_API_LIMIT", "1000")))
    parser.add_argument("--max-pages", type=int, default=int(os.getenv("MARKET_API_MAX_PAGES", "50")))
    parser.add_argument("--output", default=DEFAULT_OUT)
    args = parser.parse_args()

    if not args.resource_id:
        raise SystemExit("Missing --resource-id (or MARKET_API_RESOURCE_ID env var)")
    if not args.api_key:
        raise SystemExit("Missing --api-key (or MARKET_API_KEY env var)")

    raw_df = fetch_all_records(args.resource_id, args.api_key, args.limit, args.max_pages)
    clean_df = normalize_market_df(raw_df)

    if clean_df.empty:
        raise SystemExit("No records fetched or normalization failed. Check resource schema and API filters.")

    clean_df.to_csv(args.output, index=False)

    arrival = pd.to_datetime(clean_df["arrival_date"], errors="coerce")
    print("\nSync completed")
    print(f"Output: {args.output}")
    print(f"Rows: {len(clean_df)}")
    print(f"Date range: {arrival.min()} -> {arrival.max()}")
    print(f"Generated at: {datetime.now().isoformat(timespec='seconds')}")


if __name__ == "__main__":
    main()
