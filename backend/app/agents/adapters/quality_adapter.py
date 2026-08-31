class QualityAdapter:
    """
    Quality Inspection Adapter for report consolidation.
    
    IMPORTANT: This adapter currently generates context-sensitive mock data
    for the demonstration. It is designed to be easily replaced by your teammate's
    actual Quality Inspection Agent endpoint.
    """
    @staticmethod
    def get_results(project_id: str) -> dict:
        if project_id == "P001":
            return {
                "defects_detected": 2,
                "critical_defects": 1,
                "quality_status": "Attention Required",
                "summary": "Concrete curing cracks identified on columns; steel structural alignment requires adjustment.",
                "is_mock_data": True
            }
        elif project_id == "P002":
            return {
                "defects_detected": 0,
                "critical_defects": 0,
                "quality_status": "Passed",
                "summary": "Foundation footings and wall curing passed inspection limits.",
                "is_mock_data": True
            }
        elif project_id == "P003":
            return {
                "defects_detected": 1,
                "critical_defects": 0,
                "quality_status": "Passed with Notes",
                "summary": "Minor surface honeycombing detected on piers; structural capacity is unaffected.",
                "is_mock_data": True
            }
        else:
            return {
                "defects_detected": 1,
                "critical_defects": 0,
                "quality_status": "Passed",
                "summary": "Routine spot checks completed; only minor aesthetic finish items noted.",
                "is_mock_data": True
            }
