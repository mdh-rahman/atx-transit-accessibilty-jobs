from pathlib import Path
import argparse
import sys

import matplotlib.pyplot as plt
import pandas as pd


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
    parser.add_argument("--countyfp", default="453", help="County FIPS filter for county-level map (default: Travis=453)")
    return parser.parse_args()


def save_map(gdf, column: str, title: str, output_path: Path, cmap: str = "viridis") -> None:
    fig, ax = plt.subplots(figsize=(10, 10))
    gdf.plot(column=column, cmap=cmap, legend=True, linewidth=0.2, edgecolor="white", ax=ax)
    ax.set_axis_off()
    ax.set_title(title)
    plt.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


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
            f"Comparison file not found: {comparison_csv}. Run scripts/run_compare.py with --wac-2017 and --wac-2022 first."
        )

    comparison = pd.read_csv(comparison_csv, dtype={"from_id": "str"})
    tracts = load_capmetro_tracts(year=args.tract_year)
    tracts["GEOID"] = tracts["GEOID"].astype(str)

    merged = tracts.merge(comparison, how="left", left_on="GEOID", right_on="from_id")

    for column in ["C000_before", "C000_new", "diff"]:
        if column in merged.columns:
            merged[column] = pd.to_numeric(merged[column], errors="coerce")

    save_map(
        merged,
        column="C000_before",
        title="Transit-Accessible Jobs (2017)",
        output_path=maps_dir / "jobs_access_2017.png",
        cmap="viridis",
    )
    save_map(
        merged,
        column="C000_new",
        title="Transit-Accessible Jobs (2025)",
        output_path=maps_dir / "jobs_access_2025.png",
        cmap="viridis",
    )
    save_map(
        merged,
        column="diff",
        title="Change in Transit-Accessible Jobs (2025 - 2017)",
        output_path=maps_dir / "jobs_access_change_region.png",
        cmap="RdBu",
    )

    county_subset = merged[merged["COUNTYFP"].astype(str) == str(args.countyfp)]
    if not county_subset.empty:
        save_map(
            county_subset,
            column="diff",
            title=f"Change in Transit-Accessible Jobs (CountyFP {args.countyfp})",
            output_path=maps_dir / f"jobs_access_change_county_{args.countyfp}.png",
            cmap="RdBu",
        )

    print("Map outputs written to:")
    print(maps_dir.resolve())
