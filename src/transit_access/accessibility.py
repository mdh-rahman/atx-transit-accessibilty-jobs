import pandas as pd


def summarize_jobs_within_threshold(
    travel_times: pd.DataFrame,
    jobs_by_tract: pd.DataFrame,
    threshold_minutes: int = 45,
    from_col: str = "from_id",
    to_col: str = "to_id",
    jobs_col: str = "C000",
) -> pd.DataFrame:
    filtered = travel_times[travel_times["travel_time"] < threshold_minutes]
    merged = filtered.merge(jobs_by_tract, how="left", left_on=to_col, right_on="tract_id")
    summary = merged.groupby(from_col, as_index=False)[jobs_col].sum()
    return summary


def compare_accessibility(before_df: pd.DataFrame, new_df: pd.DataFrame, id_col: str = "from_id") -> pd.DataFrame:
    out = before_df.merge(new_df, how="outer", on=id_col, suffixes=("_before", "_new"))
    out["diff"] = out["C000_new"] - out["C000_before"]
    return out


def build_accessibility_comparison(
    travel_times_before: pd.DataFrame,
    travel_times_new: pd.DataFrame,
    jobs_before: pd.DataFrame,
    jobs_new: pd.DataFrame,
    threshold_minutes: int = 45,
) -> pd.DataFrame:
    acc_before = summarize_jobs_within_threshold(
        travel_times=travel_times_before,
        jobs_by_tract=jobs_before,
        threshold_minutes=threshold_minutes,
    )
    acc_new = summarize_jobs_within_threshold(
        travel_times=travel_times_new,
        jobs_by_tract=jobs_new,
        threshold_minutes=threshold_minutes,
    )
    return compare_accessibility(before_df=acc_before, new_df=acc_new, id_col="from_id")


def merge_comparison_to_tracts(
    tracts_df: pd.DataFrame,
    comparison_df: pd.DataFrame,
    tract_geoid_col: str = "GEOID",
    comparison_id_col: str = "from_id",
) -> pd.DataFrame:
    return tracts_df.merge(comparison_df, how="left", left_on=tract_geoid_col, right_on=comparison_id_col)
