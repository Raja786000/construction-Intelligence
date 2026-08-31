class RiskAdapter:
    """
    Risk Assessment Adapter for report consolidation.
    
    IMPORTANT: This adapter currently generates context-sensitive mock data
    for the demonstration. It is designed to be easily replaced by your teammate's
    actual Risk Assessment Agent endpoint.
    """
    @staticmethod
    def get_results(project_id: str) -> dict:
        if project_id == "P001":
            return {
                "risk_score": 64,
                "risk_level": "Medium",
                "weather_risk": "Moderate",
                "summary": "Incoming rain forecast may impact open-air steel framing work.",
                "is_mock_data": True
            }
        elif project_id == "P002":
            return {
                "risk_score": 18,
                "risk_level": "Low",
                "weather_risk": "Low",
                "summary": "Favorable dry weather conditions; no major environmental risks.",
                "is_mock_data": True
            }
        elif project_id == "P003":
            return {
                "risk_score": 12,
                "risk_level": "Low",
                "weather_risk": "Low",
                "summary": "Optimal wind and visibility speeds for excavation and compaction.",
                "is_mock_data": True
            }
        else:
            return {
                "risk_score": 30,
                "risk_level": "Low",
                "weather_risk": "Low",
                "summary": "Standard site risk parameters within acceptable limits.",
                "is_mock_data": True
            }
