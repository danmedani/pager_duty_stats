from pager_duty_stats.logic.incident_types import extract_incident_type
from pager_duty_stats.logic.incident_types import ExtractionTechnique


def test_extract_incident_type_title():
    assert extract_incident_type(
        incident={
            'title': 'Some Title'
        },
        extraction_technique=ExtractionTechnique.TITLE
    ) == 'Some Title'


def test_extract_incident_type_yc_part_2():
    assert extract_incident_type(
        incident={
            'title': 'Title Part 1 : Title Part 2 : Title Part 3'
        },
        extraction_technique=ExtractionTechnique.YC
    ) == 'Title Part 2'


def test_extract_incident_type_yc():
    assert extract_incident_type(
        incident={
            'title': 'Only One Part'
        },
        extraction_technique=ExtractionTechnique.YC
    ) == 'Only One Part'


def test_extraction_technique_str():
    assert str(ExtractionTechnique.TITLE) == 'title'
