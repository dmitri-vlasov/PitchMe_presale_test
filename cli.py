import argparse
from pathlib import Path


def cli_interface() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="HR tool to match available profiles against given target profile specified"
    )
    parser.add_argument(
        "--filter",
        required=True,
        type=str,
        help="Specify one of the target profiles in HR config",
    )
    parser.add_argument("--input", type=Path, help="Path to JSON profiles")

    return parser
