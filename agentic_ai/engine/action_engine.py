def formulate_recommendations(question: str, data_result: dict = None, ml_result: dict = None, support_result: dict = None) -> dict:
    """
    Recommendation & Action Engine: Formulate business recommendations
    based on combined evidence from Data, ML predictions, and Support Policy.
    """
    recommendations = []
    approval_required = False
    action_type = "NONE"
    target_entity = None

    # Check ML predictions for high risk driver
    if ml_result and "predictions" in ml_result:
        preds = ml_result["predictions"]
        if preds.get("found") and preds.get("mode") != "batch":
            risk_lvl = preds.get("risk_level")
            d_id = preds.get("driver_id")
            d_name = preds.get("driver_name", d_id)
            target_entity = d_id

            if risk_lvl == "High":
                recommendations.append(
                    f"ASSIGN TRAINING: Driver {d_name} ({d_id}) is at High Risk. Assign mandatory 'Customer Service & Hospitality Coaching' module."
                )
                approval_required = True
                action_type = "ASSIGN_TRAINING"
            elif risk_lvl == "Medium":
                recommendations.append(
                    f"MONITOR & REVIEW: Driver {d_name} ({d_id}) is at Medium Risk. Schedule operational review within 7 days."
                )

        elif preds.get("mode") == "batch":
            top_high = preds.get("top_high_risk_drivers", [])
            if top_high:
                top_driver = top_high[0]
                recommendations.append(
                    f"OPERATIONAL ACTION: Review top high-risk drivers starting with {top_driver['driver_name']} ({top_driver['driver_id']}) - Risk Probability: {round(top_driver['risk_probability']*100, 1)}%."
                )

    # Check support results for SOP guidelines
    if support_result and support_result.get("sources"):
        recommendations.append(
            "COMPLIANCE ACTION: Ensure all operational procedures follow the retrieved support policies."
        )

    if not recommendations:
        recommendations.append("INFORMATIONAL: No specific operational action required for this query.")

    return {
        "recommendations": recommendations,
        "primary_recommendation": recommendations[0] if recommendations else "No action required.",
        "approval_required": approval_required,
        "action_type": action_type,
        "target_entity": target_entity
    }
