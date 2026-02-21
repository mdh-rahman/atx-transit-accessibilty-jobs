from pathlib import Path


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[1]
    print("Run 2017 pipeline here.")
    print(f"Project root: {project_root}")
