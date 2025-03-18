"""
Prompt template management system
"""
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Dictionary of available prompt templates
PROMPT_TEMPLATES = {
    "default_tasks": """
        You are a task planning AI. Create a list of 3-5 tasks to achieve this objective: {objective}.
        Available abilities: [text-completion] only.
        Format as JSON array with these fields for each task:
        - id: sequential number starting at 1
        - task: detailed description of what to do
        - ability: always 'text-completion'
        - dependent_task_ids: empty array or array of task IDs this depends on
        - status: always 'incomplete'
        The final task should always be to create a summary report of all findings.
        Example: [{"id": 1, "task": "Research top attractions in Bangkok", "ability": "text-completion", "dependent_task_ids": [], "status": "incomplete"}]
    """,

    "marketing_insights": """
    You are an expert marketing AI consultant. Create a list of 3-5 specific, data-driven insights to help achieve this objective: {objective}.
    Available abilities: [text-completion] only.
    Each insight should be highly actionable and lead to a specific, measurable marketing improvement.
    Format as JSON array with these fields for each insight:
    - id: sequential number starting at 1
    - insight: detailed description of the marketing finding and its business impact
    - action_item: specific, concrete steps the shop owner should take to implement this insight
    - expected_outcome: measurable results the shop owner can expect
    - implementation_difficulty: rated as 'easy', 'medium', or 'hard'
    - priority: rated as 'high', 'medium', or 'low' based on potential impact
    - ability: always 'text-completion'
    - dependent_insight_ids: empty array or array of insight IDs this depends on
    - status: always 'ready_to_implement'
    The final insight should always connect all previous insights into a cohesive marketing strategy.
    Example: [{"id": 1, "insight": "Analysis shows 68% of abandoned carts occur during the shipping cost reveal, indicating price sensitivity", "action_item": "Implement a free shipping threshold at $50 and highlight progress toward free shipping on product pages", "expected_outcome": "15-20% reduction in cart abandonment rate and 10% increase in average order value", "implementation_difficulty": "medium", "priority": "high", "ability": "text-completion", "dependent_insight_ids": [], "status": "ready_to_implement"}]
    """,

    "propensity_modeling": """
    You are an expert marketing analytics consultant specializing in propensity modeling. Your task is to create a highly personalized email newsletter campaign targeting 10 specific customers based on their purchase history and behavioral data related to this objective: {objective}.
    Available abilities: [text-completion] only.
    Using propensity matching techniques, analyze the customer database to identify the perfect product recommendation for each customer.
    Format as JSON array with these fields for the email campaign:
    - campaign_id: unique identifier for this newsletter campaign
    - campaign_name: catchy, descriptive name for the campaign
    - subject_line: compelling email subject line with personalization
    - recommendations: array of 10 customer-product pairings with these fields for each:
      - customer_id: integer identifier for the customer
      - customer_segment: brief description of this customer's category/profile
      - purchase_history_summary: brief overview of relevant past purchases
      - recommended_product_id: product identifier
      - recommended_product_name: name of the recommended product
      - propensity_score: number between 0.1-1.0 indicating likelihood of purchase
      - recommendation_rationale: detailed explanation of why this product matches this customer
      - personalized_message: short, customized text for this specific customer-product pairing
      - suggested_discount: recommended discount percentage if appropriate
    - expected_campaign_metrics: projection of open rate, click rate, and conversion rate
    - follow_up_strategy: brief description of how to measure results and iterate
    Ensure recommendations use realistic product types and customer behaviors. Incorporate affinity analysis, look-alike modeling principles, and predictive targeting techniques in your rationales.
    Example: {"campaign_id": "PM2025-03", "campaign_name": "Spring Personalized Picks", "subject_line": "{{FirstName}}, We've Found Your Perfect Match", "recommendations": [{"customer_id": 1, "customer_segment": "Luxury Beauty Enthusiast", "purchase_history_summary": "Frequently purchases high-end skincare, focus on anti-aging", "recommended_product_id": "SK-447", "recommended_product_name": "Premium Vitamin C Serum", "propensity_score": 0.89, "recommendation_rationale": "Based on previous purchases of complementary serums and browsing history focused on brightening products", "personalized_message": "Your skincare routine is missing this perfect finishing touch!", "suggested_discount": "0%"}]}
    """
}

def get_prompt_template(template_name: str, **kwargs: Any) -> str:
    """Get a prompt template and format it with the provided kwargs"""
    template = PROMPT_TEMPLATES.get(template_name)
    if not template:
        logger.warning(f"Template '{template_name}' not found, using default")
        template = PROMPT_TEMPLATES.get("default_tasks")

    # Create a dictionary with all the keys in lowercase
    lowercase_kwargs = {k.lower(): v for k, v in kwargs.items()}

    try:
        # Replace placeholders manually to avoid issues with JSON braces
        result = template
        for key, value in lowercase_kwargs.items():
            placeholder = "{" + key + "}"
            if placeholder in result:
                result = result.replace(placeholder, str(value))
            else:
                logger.warning(f"Placeholder '{placeholder}' not found in template")

        # Check if any placeholders remain
        import re
        remaining_placeholders = re.findall(r'\{([^{}]+)\}', result)
        if remaining_placeholders:
            logger.warning(f"Unreplaced placeholders in template: {remaining_placeholders}")

        return result.strip()
    except Exception as e:
        logger.error(f"Error formatting template: {e}")
        return template.strip()  # Return unformatted as fallback

def add_prompt_template(name: str, template: str) -> None:
    """Add a new prompt template"""
    PROMPT_TEMPLATES[name] = template
    logger.info(f"Added new prompt template: {name}")