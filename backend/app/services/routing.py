from app.models.lead import LeadScore, RoutingDecision

class RoutingService:
    """
    Service for routing leads based on their score.
    """

    # These thresholds could be moved to config.py to be loaded from the environment
    # for even better configurability without code changes.
    HOT_LEAD_THRESHOLD = 85
    WARM_LEAD_THRESHOLD = 60

    def route_lead(self, lead_score: LeadScore) -> RoutingDecision:
        """
        Routes a lead to the appropriate queue based on their score.
        """
        score = lead_score.score
        category = lead_score.category

        if category == "Hot" and score >= self.HOT_LEAD_THRESHOLD:
            return RoutingDecision(
                queue="Sales",
                reason=f"Lead is Hot with a score of {score}. Assigned directly to sales team."
            )
        elif category == "Warm" and score >= self.WARM_LEAD_THRESHOLD:
            return RoutingDecision(
                queue="Presales",
                reason=f"Lead is Warm with a score of {score}. Assigned to presales for further qualification."
            )
        else:
            return RoutingDecision(
                queue="Nurture",
                reason=f"Lead is Cold with a score of {score}. Added to nurture campaign."
            )

routing_service = RoutingService()
