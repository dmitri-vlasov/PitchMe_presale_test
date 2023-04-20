import json
import sys
from pathlib import Path
from typing import List

import pydantic

import config
from cli import cli_interface
from match_service.profile_schema import Profile
from match_service.specifications import chain_specifications_for_position


def main() -> None:
    cli_parser = cli_interface()

    args = cli_parser.parse_args()
    # get candidate profiles to be checked
    profiles_file_path = args.input
    # get job descriptions specified by HR based on client needs
    target_position_name = args.filter

    if not profiles_file_path:
        profiles_file_path = Path(__file__).parent / config.TEST_PROFILES_FILE
    if not profiles_file_path.exists() or not profiles_file_path.is_file():
        sys.exit(f'Error: file with available profiles is not found')

    target_positions_path = Path(__file__).parent / config.TARGET_POSITIONS_CONFIG_FILE
    if not target_positions_path.exists() or not target_positions_path.is_file():
        sys.exit(f'Error: file with available target positions is not found')

    # Use iterative JSON parser for large JSON inputs (e.g. ijson library) in production environment
    target_positions = json.load(open(target_positions_path))
    try:
        target_position_criteria = target_positions[target_position_name]
    except KeyError:
        sys.exit(
            'There are no target positions found with specified name. Add one first to perform a search'
        )

    # build target specification to apply to each profile
    target_specification = chain_specifications_for_position(target_position_criteria)

    # parse given profiles
    available_profiles = []
    # Use iterative JSON parser for large JSON inputs (e.g. ijson library) in production environment
    for profile in json.load(open(profiles_file_path)):
        try:
            valid_profile = Profile(**profile)
        except pydantic.ValidationError:
            print("Candidate provided invalid data - profile will not be considered.")
        else:
            available_profiles.append(valid_profile)

    # perform checks on each profile
    for profile in available_profiles:
        if target_specification.is_satisfied_by(profile):
            print(f"{profile.first_name} {profile.last_name} - True")


if __name__ == '__main__':
    main()
