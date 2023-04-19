from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Iterable, List, Literal, Union

from match_service import constants, profile_schema, utils


class SelectionCriteria(Enum):
    EMPLOYER = 'employer'
    LOCATION = 'location'
    EXPERIENCE_TOTAL = 'experience_total'
    SKILLS = 'skills'
    SKILLS_AT_WORK = 'skills_at_work'
    POSITION = 'position'
    DURATION_OF_EMPLOYMENT = 'duration_of_employment'


class BaseSpecification(ABC):
    """
    https://en.wikipedia.org/wiki/Specification_pattern
    """

    @abstractmethod
    def is_satisfied_by(self, candidate: profile_schema.Profile) -> bool:
        ...

    def and_(self, other: BaseSpecification) -> AndSpecification:
        return AndSpecification(self, other)


@dataclass(frozen=True)
class AndSpecification(BaseSpecification):
    first: BaseSpecification
    second: BaseSpecification

    def is_satisfied_by(self, candidate: profile_schema.Profile) -> bool:
        return self.first.is_satisfied_by(candidate) and self.second.is_satisfied_by(
            candidate
        )


@dataclass
class EmployerNameSpecification(BaseSpecification):
    """
    Checks whether at least one of the positions held during
    last n experiences was with one of the expected companies.
    """

    companies_expected: utils.LowerCaseFrozenSet[str]
    number_of_last_experiences_to_be_checked: int

    def is_satisfied_by(self, candidate: profile_schema.Profile) -> bool:
        experiences_to_be_checked = candidate.get_n_last_experiences(
            self.number_of_last_experiences_to_be_checked
        )
        employer_names = utils.LowerCaseFrozenSet(
            {experience.company_name for experience in experiences_to_be_checked}
        )

        employer_name_criteria_is_met = bool(
            len(employer_names.intersection(self.companies_expected))
        )

        if employer_name_criteria_is_met:
            return True

        print(
            f"{candidate.first_name} {candidate.last_name} - False, "
            f"Didn't work the following companies: {', '.join(self.companies_expected)} during the last "
            f"{self.number_of_last_experiences_to_be_checked} work experiences."
        )
        return False


@dataclass
class LocationSpecification(BaseSpecification):
    """
    Checks whether a candidate meets location criteria.
    """

    expected_locations: Iterable[str]

    def is_satisfied_by(self, candidate: profile_schema.Profile) -> bool:
        if (
            candidate.location.country in self.expected_locations
            or candidate.location.city in self.expected_locations
        ):
            return True

        print(
            f"{candidate.first_name} {candidate.last_name} - False, "
            f"Doesn't live in specified countries / cities."
        )
        return False


@dataclass
class TotalWorkExperienceSpecification(BaseSpecification):
    """
    Checks whether candidate's total years of experience meet
    the expected number of years requirement.
    Overlapping experiences can be counted as an option.
    """

    years_of_experience_expected: float
    comparison_operand: Literal['>', '>=', '==', '<', '<=']
    count_overlapping_experiences: bool = False

    def is_satisfied_by(self, candidate: profile_schema.Profile) -> bool:
        total_years_of_experience = candidate.count_years_of_experience(
            count_overlapping_experiences=self.count_overlapping_experiences
        )

        if utils.comparison_functions[self.comparison_operand](
            total_years_of_experience, self.years_of_experience_expected
        ):
            return True

        print(
            f"{candidate.first_name} {candidate.last_name} - False, Worked for not "
            f"{self.comparison_operand} {self.years_of_experience_expected} years."
        )
        return False


@dataclass
class SkillsSpecification(BaseSpecification):
    """
    Checks whether candidate skills match the required number of expected skills
    """

    expected_skills: utils.LowerCaseFrozenSet[str]
    number_of_hits: Union[int, None] = None

    def is_satisfied_by(self, candidate: profile_schema.Profile) -> bool:
        skills_to_be_checked = utils.LowerCaseFrozenSet(candidate.skills)

        skills_criteria_is_met = utils.has_intersection_or_is_subset(
            skills_to_be_checked,
            self.expected_skills,
            number_of_hits=self.number_of_hits,
        )

        if skills_criteria_is_met:
            return True

        print(
            f"{candidate.first_name} {candidate.last_name} - False, Doesn't have the required skill set"
        )
        return False


@dataclass
class SkillsAtWorkSpecification(BaseSpecification):
    """
    Checks whether candidate skills during last n experiences
    match the required number of expected skills
    """

    expected_skills: utils.LowerCaseFrozenSet[str]
    number_of_last_experiences_to_be_checked: int
    number_of_hits: Union[int, None] = None

    def is_satisfied_by(self, candidate: profile_schema.Profile) -> bool:
        experiences_to_be_checked = candidate.get_n_last_experiences(
            self.number_of_last_experiences_to_be_checked
        )

        skills_to_be_checked = set()
        for experience in experiences_to_be_checked:
            for skill in experience.skills:
                skills_to_be_checked.add(skill)
        skills_to_be_checked = utils.LowerCaseFrozenSet(skills_to_be_checked)

        skills_criteria_is_met = utils.has_intersection_or_is_subset(
            skills_to_be_checked,
            self.expected_skills,
            number_of_hits=self.number_of_hits,
        )

        if skills_criteria_is_met:
            return True

        print(
            f"{candidate.first_name} {candidate.last_name} - "
            f"False, Skill set during last n experiences doesn't match expected skills"
        )
        return False


@dataclass
class PositionSpecification(BaseSpecification):
    """
    Checks whether at least one of the positions held during
    last n experiences matches one of the expected positions.
    """

    positions_expected: utils.LowerCaseFrozenSet[str]
    number_of_last_experiences_to_be_checked: int

    def is_satisfied_by(self, candidate: profile_schema.Profile) -> bool:
        experiences_to_be_checked = candidate.get_n_last_experiences(
            self.number_of_last_experiences_to_be_checked
        )
        positions_held = utils.LowerCaseFrozenSet(
            {experience.job_title for experience in experiences_to_be_checked}
        )

        occupied_position_criteria_is_met = bool(
            len(positions_held.intersection(self.positions_expected))
        )

        if occupied_position_criteria_is_met:
            return True

        print(
            f"Didn't occupy the following positions: {', '.join(self.positions_expected)} during the last "
            f"{self.number_of_last_experiences_to_be_checked} work experiences."
        )
        return False


@dataclass
class WorkExperienceLengthSpecification(BaseSpecification):
    """
    Checks whether candidate's years of experience during n last
    positions held meets the expected number of years requirement for
    at least one of those n last experiences.
    """

    years_of_experience_expected: int
    comparison_operand: Literal['>', '>=', '==', '<', '<=']
    number_of_last_experiences_to_be_checked: int = 1

    def is_satisfied_by(self, candidate: profile_schema.Profile) -> bool:
        last_n_experiences = candidate.get_n_last_experiences(
            self.number_of_last_experiences_to_be_checked
        )

        longest_experience = max(
            last_n_experiences,
            key=lambda experience: int(
                (experience.ends_at - experience.starts_at).days
            ),
        )

        longest_experience_in_days = int(
            (longest_experience.ends_at - longest_experience.starts_at).days
        )
        longest_experience_in_years = round(
            longest_experience_in_days / constants.NUMBER_OF_DAYS_IN_ONE_YEAR, 1
        )

        if utils.comparison_functions[self.comparison_operand](
            longest_experience_in_years, self.years_of_experience_expected
        ):
            return True

        print(
            f"Worked for not {self.comparison_operand} {self.years_of_experience_expected} during last "
            f"{self.number_of_last_experiences_to_be_checked} experiences."
        )
        return False


def specification_factory(
    criteria_name: str, criteria_value: Union[str, dict, List[str]]
) -> Union[BaseSpecification, None]:
    """
    Maps HR config values to specifications
    and returns instances of BaseSpecification.
    """
    # check whether the number of experiences to be checked (as per target
    # position requirements) (if such criteria is present) is greater than or equal to one
    if 'check_last_n_experiences' in criteria_value:
        check_last_n_experiences = criteria_value['check_last_n_experiences']

        if check_last_n_experiences < 1:
            raise ValueError(
                f'Specified number (n) of last experiences should be >= 1, '
                f'but {check_last_n_experiences} is given. Fix the target_position_config and retry'
            )

    # instantiate particular specification based on criteria name
    if criteria_name == SelectionCriteria.EMPLOYER.value:
        if criteria_value['name'] == 'FAANG':
            companies_expected = constants.FAANG
        else:
            companies_expected = utils.LowerCaseFrozenSet({criteria_value['name']})

        return EmployerNameSpecification(
            companies_expected=companies_expected,
            number_of_last_experiences_to_be_checked=criteria_value[
                'check_last_n_experiences'
            ],
        )

    elif criteria_name == SelectionCriteria.LOCATION.value:
        if not criteria_value['countries'] and not criteria_value['cities']:
            raise ValueError(f'Specify either country or city within location criteria')

        if criteria_value['countries']:
            for index, country in enumerate(criteria_value['countries']):
                countries = {*criteria_value['countries']}
                if country.upper() == 'EU':
                    countries = {
                        *criteria_value['countries'][:index],
                        *constants.EU_COUNTRIES,
                        *criteria_value['countries'][index + 1 :],
                    }
                return LocationSpecification(countries)
        else:
            cities = {*criteria_value['cities']}
            return LocationSpecification(cities)

    elif criteria_name == SelectionCriteria.EXPERIENCE_TOTAL.value:
        return TotalWorkExperienceSpecification(
            years_of_experience_expected=criteria_value['years'],
            comparison_operand=criteria_value['comparison_operand'],
        )

    elif criteria_name == SelectionCriteria.SKILLS.value:
        return SkillsSpecification(
            expected_skills=utils.LowerCaseFrozenSet(criteria_value['name']),
            number_of_hits=criteria_value.get('number_of_hits', None),
        )

    elif criteria_name == SelectionCriteria.SKILLS_AT_WORK.value:
        return SkillsAtWorkSpecification(
            expected_skills=utils.LowerCaseFrozenSet(criteria_value['name']),
            number_of_hits=criteria_value.get('number_of_hits', None),
            number_of_last_experiences_to_be_checked=criteria_value.get(
                'check_last_n_experiences'
            ),
        )

    elif criteria_name == SelectionCriteria.POSITION.value:
        return PositionSpecification(
            positions_expected=utils.LowerCaseFrozenSet(criteria_value['name']),
            number_of_last_experiences_to_be_checked=criteria_value.get(
                'check_last_n_experiences'
            ),
        )

    elif criteria_name == SelectionCriteria.DURATION_OF_EMPLOYMENT.value:
        return WorkExperienceLengthSpecification(
            years_of_experience_expected=criteria_value['years'],
            comparison_operand=criteria_value['comparison_operand'],
            number_of_last_experiences_to_be_checked=criteria_value[
                'check_last_n_experiences'
            ],
        )
    else:
        print(
            f'Criteria name "{criteria_name}" specified in config '
            f'is not supported, therefore, will be ignored'
        )


def chain_specifications_for_position(
    target_profile_criteria: dict[str, Union[str, List[str]]]
) -> BaseSpecification:
    """
    Chains specifications for a position according to the specified set of criteria.
    """
    specifications = []
    for criteria_name, criteria_value in target_profile_criteria.items():
        specification = specification_factory(criteria_name, criteria_value)
        if specification:
            specifications.append(specification)
    try:
        target_specification = specifications[0]
    except IndexError:
        raise ValueError('Please specify at least one valid target profile criteria')

    for i in range(1, len(specifications)):
        target_specification = target_specification.and_(specifications[i])

    return target_specification
