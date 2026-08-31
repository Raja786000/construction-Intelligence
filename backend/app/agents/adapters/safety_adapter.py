class SafetyAdapter:
    """
    Safety Adapter for report consolidation.
    
    IMPORTANT: This adapter currently generates context-sensitive mock data
    for the demonstration. It is designed to be easily replaced by a direct 
    API call or graph invocation to your teammates' YOLO Safety Agent.
    """
    @staticmethod
    def get_results(project_id: str) -> dict:
        # Mock Safety data mapped to demo projects
        if project_id == "P001":
            return {
                "ppe_violations": 4,
                "helmet_violations": 3,
                "vest_violations": 1,
                "critical_safety_events": 0,
                "summary": "Multiple PPE violations detected in Zone B (framing area).",
                "is_mock_data": True
            }
        elif project_id == "P002":
            return {
                "ppe_violations": 0,
                "helmet_violations": 0,
                "vest_violations": 0,
                "critical_safety_events": 0,
                "summary": "All workers are fully compliant with mandatory safety wear.",
                "is_mock_data": True
            }
        elif project_id == "P003":
            return {
                "ppe_violations": 1,
                "helmet_violations": 1,
                "vest_violations": 0,
                "critical_safety_events": 0,
                "summary": "One helmet violation was detected in Zone A and resolved immediately.",
                "is_mock_data": True
            }
        else:
            # Fallback mock safety results for other project IDs
            return {
                "ppe_violations": 2,
                "helmet_violations": 1,
                "vest_violations": 1,
                "critical_safety_events": 0,
                "summary": "Periodic minor PPE violations observed during shift change.",
                "is_mock_data": True
            }
