from datetime import date
from typing import List, Literal, Optional

from pydantic import BaseModel, root_validator

from match_service import constants, utils


class Location(BaseModel):
    city: str
    country: str


class Experience(BaseModel):
    company_name: str
    job_title: str
    description: str
    skills: List[str]
    starts_at: date
    ends_at: Optional[date]
    location: Location


class Profile(BaseModel):
    first_name: str
    last_name: str
    skills: List[str]
    description: str
    location: Location
    experiences: List[Experience]

    @root_validator
    def check_start_date_precedes_end_date(cls, values):
        """
        Checks whether particular experience's 'starts_at' date precedes 'ends_at' date.
        If not - that particular experience will be ignored.
        If 'ends_at' field is None, we assume that the experience in question is ongoing
        and populate 'ends_at' with today's date.
        """
        experiences = values.get('experiences')
        for idx, experience in enumerate(experiences):
            if not experience.ends_at:
                experience.ends_at = date.today()

            if experience.starts_at >= experience.ends_at:
                print(
                    f'{values.get("first_name")} {values.get("last_name")} - Position {experience.job_title} at '
                    f'{experience.company_name} "starts_at" date must precede the "ends_at" date and thus the '
                    f'experience will be ignored'
                )
                del experiences[idx]

        return values

    def get_n_last_experiences(self, n: int) -> List[Experience]:
        """
        Accepts candidate's sorted (by 'ends_at') experiences and lists a specified number (n) of last experiences.
        Used further to determine whether a candidate:
            - worked for a certain number of years
            - worked for particular companies
            - held particular positions
            - used particular skills
        during candidate's n last experiences.
        """
        sorted_experiences = self._get_experiences_sorted_by('ends_at')
        # if a candidate has fewer experiences (or exactly as many as) than we want to check,
        # we'll return all candidate's experiences
        if len(sorted_experiences) <= n:
            return sorted_experiences

        return sorted_experiences[-1 : -n - 1 : -1]

    def count_years_of_experience(
        self, count_overlapping_experiences: bool = False
    ) -> float:
        """
        Accepts candidate's sorted (by 'starts_at') experiences and counts his/her years of experience.
        Overlapping experiences can be counted as an option.
        """
        sorted_experiences = self._get_experiences_sorted_by('starts_at')

        intervals = [
            [experience.starts_at, experience.ends_at]
            for experience in sorted_experiences
        ]
        if not count_overlapping_experiences:
            intervals = utils.merge_intervals(intervals)

        # count days of experience based on time intervals
        days_of_experience = 0

        for start, end in intervals:
            days_of_experience_with_a_company = int((end - start).days)
            days_of_experience += days_of_experience_with_a_company

        # count years of experience based on average number of days in a year and floor rounding
        years_of_experience = round(
            days_of_experience / constants.NUMBER_OF_DAYS_IN_ONE_YEAR, 1
        )
        return years_of_experience

    def _get_experiences_sorted_by(
        self, sorting_criteria: Literal['starts_at', 'ends_at']
    ) -> List[Experience]:
        """
        Sorts experiences by as per the selected sort criteria ('starts_at' or 'ends_at') in ascending order.
        """
        return sorted(
            self.experiences,
            key=lambda experience: getattr(experience, sorting_criteria),
        )
