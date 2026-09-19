from app.models.agent_state import SafetyAgentState
from app.tools.safety_tool import safety_detection_tool
from app.config.gemini import llm

def detect_safety(state: SafetyAgentState):

    print("\n========== TOOL NODE ==========")

    result = safety_detection_tool(
        state["image_path"]
    )

    state["detections"] = result["detections"]
    state["output_image"]=result["output_image"]

    return state

def analyze_detection(state: SafetyAgentState):

    print("========== ANALYZE NODE ==========")
    print(state["detections"])

    return state

def assess_risk(state: SafetyAgentState):

    print("\n========== RISK NODE ==========")

    detections = state["detections"]

    persons = detections.get("Person", 0)

    no_vest = detections.get("NO-Safety Vest", 0)

    no_mask = detections.get("NO-Mask", 0)

    no_hardhat = persons - detections.get("Hardhat", 0)

    violations = no_vest + no_mask + max(no_hardhat, 0)

    if violations == 0:
        risk = "LOW"

    elif violations <= 3:
        risk = "MEDIUM"

    else:
        risk = "HIGH"

    state["risk_level"] = risk

    print("Risk Level :", risk)

    return state

def _generate_rule_based_recommendation(detections: dict, risk: str, compliance=None) -> str:
    no_hardhat = detections.get("NO-Hardhat", 0)
    no_vest = detections.get("NO-Safety Vest", 0)
    no_mask = detections.get("NO-Mask", 0)

    actions = []
    if no_hardhat > 0:
        actions.append(f"Issue immediate hardhat mandate for {no_hardhat} personnel observed in active zones.")
    if no_vest > 0:
        actions.append(f"Enforce high-visibility safety vest compliance across {no_vest} identified workers.")
    if not actions:
        actions.append("Maintain standard protocols; verified full PPE compliance across inspected zone.")

    comp_str = f"\n**Compliance Score:** {compliance}%\n" if compliance is not None else ""

    return f"""### Professional Safety Recommendation
**Risk Assessment:** {risk}{comp_str}

1. **Immediate Corrective Actions:**
{chr(10).join([f"   - {a}" for a in actions])}

2. **Preventive Measures:**
   - Conduct daily pre-shift Toolbox Talk emphasizing personal protective equipment.
   - Restrict access to designated high-risk zones without verified mandatory gear.

3. **Safety Advice:**
   - Safety gear compliance is mandatory for all personnel and sub-contractors on site.
"""

def generate_recommendation(state: SafetyAgentState):

    print("\n========== RECOMMENDATION NODE ==========")

    detections = state["detections"]
    risk = state["risk_level"]

    compliance = state.get("compliance_score")

    if compliance is not None:
        prompt = f"""You are an experienced Construction Safety Officer.
Analyze the following CCTV video safety monitoring results.
Detected Objects: {detections}
Compliance Score: {compliance}%
Overall Risk Level: {risk}

Generate a SHORT professional construction safety recommendation.
Include:
1. Professional Safety Recommendation
2. Immediate Corrective Actions
3. Preventive Measures
4. Short Safety Advice
Keep the response concise and practical."""
    else:
        prompt = f"""You are an experienced Construction Safety Officer.
Analyze the following PPE detection results.
Detected Objects: {detections}
Overall Risk Level: {risk}

Generate a SHORT professional safety recommendation.
Include:
1. Professional Safety Recommendation
2. Immediate Corrective Actions
3. Preventive Measures
4. Short Safety Advice
Keep the response concise and practical."""

    recommendation = ""
    if llm is not None:
        try:
            response = llm.invoke(prompt)
            if hasattr(response, "content") and response.content:
                recommendation = str(response.content)
            elif hasattr(response, "text") and response.text:
                recommendation = str(response.text)
            else:
                recommendation = str(response)
        except Exception as e:
            print(f"Notice: Gemini LLM invocation failed ({e}). Using rule-based safety recommendation.")
            recommendation = ""

    if not recommendation:
        recommendation = _generate_rule_based_recommendation(detections, risk, compliance)

    state["recommendation"] = recommendation
    print(recommendation)

    return state

def generate_report(state: SafetyAgentState):

    print("\n========== REPORT NODE ==========")

    detections = state["detections"].copy()

# Basic construction PPE considered mandatory
    required_detections = {
        key: value
        for key, value in detections.items()
        if key not in ["NO-Mask"]
    }


    risk = state["risk_level"]

    compliance = state.get("compliance_score")

    report = "# Construction Safety Report\n\n"

    report += "## Detection Summary\n\n"

    for name, count in detections.items():
        report += f"- **{name}** : {count}\n"

    report += "\n## Overall Risk\n\n"
    report += f"**{risk}**\n\n"

    if compliance is not None:

        report += "## Compliance Score\n\n"
        report += f"**{compliance}%**\n\n"

        analyzed_frames = state.get("analyzed_frames")

        violation_frames = state.get("violation_frames")

        if analyzed_frames is not None:
            report += (
                f"Analyzed Frames: **{analyzed_frames}**\n\n"
            )

        if violation_frames is not None:
            report += (
                f"Violation Frames: **{violation_frames}**\n\n"
            )

    report += "## Inspection Status\n\n"
    report += "✅ Inspection Completed Successfully.\n\n"

    report += "## Generated By\n\n"
    report += "Safety Monitoring Agent"

    state["report"] = report

    print(report)

    return state