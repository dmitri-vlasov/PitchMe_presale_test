import unittest

from match_service import profile_schema, specifications, utils


POTENTIAL_CANDIDATE = profile_schema.Profile(
    **{
        "first_name": "Sophia",
        "last_name": "Garcia",
        "skills": ["Figma", "UX-research"],
        "description": "I'm a Middle UX Designer with 3 years of experience in creating user-centered design solutions.",
        "location": {"city": "Barcelona", "country": "Spain"},
        "experiences": [
            {
                "company_name": "BlaBlaCar",
                "job_title": "UX Designer",
                "description": "Designed and prototyped user interfaces for BlaBlaCar's mobile and web applications.",
                "skills": ["Figma", "UX-research", "Miro"],
                "starts_at": "2019-06-01",
                "ends_at": "2022-04-01",
                "location": {"city": "Barcelona", "country": "Spain"},
            },
            {
                "company_name": "Glovo",
                "job_title": "Product Designer",
                "description": "Collaborated with product managers and engineers to develop and launch new features for Glovo's mobile app.",
                "skills": ["Sketch", "UX-research"],
                "starts_at": "2017-09-01",
                "ends_at": "2019-04-01",
                "location": {"city": "Barcelona", "country": "Spain"},
            },
        ],
    }
)


class TestSpecifications(unittest.TestCase):
    def test_employer(self):
        target_specification = specifications.EmployerNameSpecification(
            companies_expected=utils.LowerCaseFrozenSet({'NASA'}),
            number_of_last_experiences_to_be_checked=15,
        )
        self.assertEqual(
            target_specification.is_satisfied_by(POTENTIAL_CANDIDATE), False
        )

    def test_location(self):
        target_specification = specifications.LocationSpecification(
            expected_locations=['Russian Federation']
        )
        self.assertEqual(
            target_specification.is_satisfied_by(POTENTIAL_CANDIDATE), False
        )

    def test_skills(self):
        target_specification = specifications.SkillsSpecification(
            expected_skills=utils.LowerCaseFrozenSet({'Unreal Engine 7', 'Cooking'}),
            number_of_hits=2,
        )
        self.assertEqual(
            target_specification.is_satisfied_by(POTENTIAL_CANDIDATE), False
        )

    def test_skills_at_work(self):
        target_specification = specifications.SkillsAtWorkSpecification(
            expected_skills=utils.LowerCaseFrozenSet({'Miro', 'Sketch'}),
            number_of_last_experiences_to_be_checked=10,
            number_of_hits=2,
        )
        self.assertEqual(
            target_specification.is_satisfied_by(POTENTIAL_CANDIDATE), True
        )

    def test_position(self):
        target_specification = specifications.PositionSpecification(
            positions_expected=utils.LowerCaseFrozenSet({'Product Designer'}),
            number_of_last_experiences_to_be_checked=10,
        )
        self.assertEqual(
            target_specification.is_satisfied_by(POTENTIAL_CANDIDATE), True
        )

    def test_total_experience(self):
        target_specification = specifications.TotalWorkExperienceSpecification(
            years_of_experience_expected=2,
            comparison_operand='>',
            count_overlapping_experiences=False,
        )
        self.assertEqual(
            target_specification.is_satisfied_by(POTENTIAL_CANDIDATE), True
        )

    def test_work_experience_length(self):
        target_specification = specifications.WorkExperienceLengthSpecification(
            years_of_experience_expected=2,
            comparison_operand='>',
            number_of_last_experiences_to_be_checked=2,
        )
        self.assertEqual(
            target_specification.is_satisfied_by(POTENTIAL_CANDIDATE), True
        )


if __name__ == '__main__':
    unittest.main()
