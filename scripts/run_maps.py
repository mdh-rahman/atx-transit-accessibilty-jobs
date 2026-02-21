from pathlib import Path
import argparse
import sys

import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate accessibility maps from processed comparison outputs.")
    parser.add_argument(
        "--comparison-csv",
        default="data/processed/accessibility_comparison.csv",
        help="Path to accessibility comparison CSV produced by scripts/run_compare.py",
    )
    parser.add_argument(
        "--maps-dir",
        default="output/maps",
        help="Directory to save generated PNG map files",
    )
    parser.add_argument("--tract-year", type=int, default=2023, help="Census tract year (default: 2023)")
    parser.add_argument("--countyfp", default="453", help="County FIPS filter for maps (default: Travis=453)")
    parser.add_argument("--threshold", type=int, default=45, help="Travel time threshold used in comparison (default: 45)")
    return parser.parse_args()


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[1]
    if str(project_root / "src") not in sys.path:
        sys.path.insert(0, str(project_root / "src"))

    from transit_access.io import load_capmetro_tracts

    args = parse_args()
    comparison_csv = project_root / args.comparison_csv
    maps_dir = project_root / args.maps_dir
    maps_dir.mkdir(parents=True, exist_ok=True)

    if not comparison_csv.exists():
        raise FileNotFoundError(
            f"Comparison file not found: {comparison_csv}. "
            "Run scripts/run_compare.py with --wac-2017, --wac-2022, --rac-2017, and --rac-2022 first."
        )

    # Load comparison data and tract geometries
    comparison = pd.read_csv(comparison_csv, dtype={"from_id": "str"})
    tracts = load_capmetro_tracts(year=args.tract_year)
    tracts["GEOID"] = tracts["GEOID"].astype(str)

    # Merge comparison data with geometries
    merged = tracts.merge(comparison, how="left", left_on="GEOID", right_on="from_id")
    merged = gpd.GeoDataFrame(merged, geometry="geometry", crs=tracts.crs)

    # Filter to specified county (default: Travis County)
    travis_map = merged[merged["COUNTYFP"] == args.countyfp].copy()

    # Check if normalized columns exist
    normalized_col_2017 = f"ALI17_{args.threshold}_n"
    normalized_col_2025 = f"ALI22_{args.threshold}_n"
    diff_col = "ALI_diff_n"

    if normalized_col_2017 not in travis_map.columns:
        print(f"Warning: {normalized_col_2017} not found. Run run_compare.py with --rac-2017 and --rac-2022 to generate normalized metrics.")
        print("Available columns:", travis_map.columns.tolist())
        sys.exit(1)

    # Convert to numeric
    travis_map[normalized_col_2017] = pd.to_numeric(travis_map[normalized_col_2017], errors="coerce")
    travis_map[normalized_col_2025] = pd.to_numeric(travis_map[normalized_col_2025], errors="coerce")
    travis_map[diff_col] = pd.to_numeric(travis_map[diff_col], errors="coerce")

    # Custom bins for normalized access (matching notebook)
    custom_bins = [0, 1, 3, 7, 15, 30, 70, 450]

    # Map 1: 2017 Low-wage Job Access (normalized)
    fig, ax = plt.subplots(figsize=(10, 10))
    travis_map.plot(
        column=normalized_col_2017,
        cmap="Blues",
        linewidth=0.4,
        edgecolor="black",
        scheme="user_defined",
        classification_kwds={"bins": custom_bins},
        legend=True,
        legend_kwds={"title": "Transit Access Score"},
        ax=ax,
    )
    ax.set_title(
        f"Low-wage Jobs Reachable in {args.threshold} Minutes by Transit per Low-wage Worker\n"
        "Estimates for 7–9 am on Friday, June 16, 2017",
        fontsize=14,
    )
    ax.set_axis_off()
    plt.tight_layout()
    fig.savefig(maps_dir / "jobs_access_2017.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {maps_dir / 'jobs_access_2017.png'}")

    # Map 2: 2025 Low-wage Job Access (normalized)
    fig, ax = plt.subplots(figsize=(10, 10))
    travis_map.plot(
        column=normalized_col_2025,
        cmap="Blues",
        linewidth=0.4,
        edgecolor="black",
        scheme="user_defined",
        classification_kwds={"bins": custom_bins},
        legend=True,
        legend_kwds={"title": "Transit Access Score"},
        ax=ax,
    )
    ax.set_title(
        f"Low-wage Jobs Reachable in {args.threshold} Minutes by Transit per Low-wage Worker\n"
        "Estimates for 7–9 am on Tuesday, April 1, 2025",
        fontsize=14,
    )
    ax.set_axis_off()
    plt.tight_layout()
    fig.savefig(maps_dir / "jobs_access_2025.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {maps_dir / 'jobs_access_2025.png'}")

    # Map 3: Change in Low-wage Job Access (normalized)
    fig, ax = plt.subplots(figsize=(10, 10))
    travis_map.plot(
        column=diff_col,
        cmap="RdBu",
        linewidth=0.3,
        edgecolor="grey",
        legend=True,
        scheme="natural_breaks",
        k=8,
        legend_kwds={"title": "Change in Access Score"},
        ax=ax,
    )
    ax.set_title(
        f"Change in Low-wage Jobs Reachable in {args.threshold} Minutes by Transit per Low-wage Worker\n(2025 - 2017)",
        fontsize=14,
    )
    ax.set_axis_off()
    plt.tight_layout()
    fig.savefig(maps_dir / "jobs_access_change_region.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {maps_dir / 'jobs_access_change_region.png'}")

    print(f"\nMap outputs written to: {maps_dir.resolve()}")

