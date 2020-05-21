from typing import Dict
from enum import Enum

class ExtractionTechnique(Enum):
	TITLE = 'title'
	YC = 'yc'

	# useful for making args human readable
	def __str__(self):
		return self.value

def extract_incident_type(
	incident: Dict,
	extraction_technique: ExtractionTechnique
) -> str:
	if extraction_technique == ExtractionTechnique.TITLE:
		return incident['title']

	if extraction_technique == ExtractionTechnique.YC:
		title_parts = incident['title'].split(' : ')
		if len(title_parts) > 1:
			return title_parts[1]
		return title_parts[0]

	raise Exception('ExtractionTechnique {} not implemented'.format(extraction_technique))
