#!/usr/bin/env python3
"""Print the latest run_id folder and list files. Optional convenience script."""

from pathlib import Path
import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="Print latest run folder and list artifacts.")
    parser.add_argument(
        "--config",
        default="configs/run.yaml",
        help="Path to run config (default: configs/run.yaml)",
    )
    parser.add_argument(
        "--drive-root",
        help="Override drive_root from config",
    )
    parser.add_argument(
        "--runs-dir",
        default="runs",
        help="Runs directory name (default: runs)",
    )
    args = parser.parse_args()

    drive_root = args.drive_root
    runs_dir = args.runs_dir

    if not drive_root and Path(args.config).exists():
        try:
            import yaml
            with open(args.config) as f:
                cfg = yaml.safe_load(f)
            drive_root = cfg.get("paths", {}).get("drive_root", "./drive")
            runs_dir = cfg.get("paths", {}).get("runs_dir", "runs")
        except Exception:
            pass

    if not drive_root:
        drive_root = "./drive"

    runs_path = Path(drive_root) / runs_dir
    if not runs_path.exists():
        print(f"No runs directory: {runs_path}")
        return

    run_folders = sorted(
        (p for p in runs_path.iterdir() if p.is_dir()),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not run_folders:
        print("No run folders yet.")
        return

    latest = run_folders[0]
    print("Latest run folder:", latest)
    print("Run ID:", latest.name)
    print("Artifacts:")
    for f in sorted(latest.iterdir()):
        size = f.stat().st_size if f.is_file() else 0
        print(f"  - {f.name} ({size} bytes)" if f.is_file() else f"  - {f.name}/")


if __name__ == "__main__":
    main()
