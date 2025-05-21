"""
services/playbook_generator.py

AI‑Driven Remediation Playbooks for RegScale CCM

This module auto‑generates step‑by‑step remediation instructions for control failures, leveraging a template engine
and (mocked) LLM assistance. It corresponds to the "AI-Driven Remediation Playbooks" feature in
`docs/FEATURE_PROPOSALS.md`.

Key functions:
- `load_templates()`: Initializes Jinja2 environment and loads remediation templates.
- `mock_llm_enhance(step_description)`: Simulates LLM-powered refinement of a generic remediation step.
- `generate_playbook(control_id, findings, environment)`: Orchestrates playbook creation:
    1. Selects a base template for the control.
    2. Populates it with context (e.g. resource identifiers, policy names).
    3. Refines each step via `mock_llm_enhance` to produce user-friendly commands or code snippets.

Why this approach?
- **Consistency:** Templates ensure remediation steps follow organizational standards (e.g. naming conventions).
- **Customization:** LLM enhancement tailors generic instructions to specific environments (AWS/Azure/GCP).
- **Automated Ticketing:** Output can be sent directly to Jira/ServiceNow APIs for immediate action.
- **Extensible:** Swap `mock_llm_enhance` with a real LLM call when available.

Usage:
    from services.playbook_generator import generate_playbook
    playbook = generate_playbook(
        control_id="AC-2",
        findings={"ResourceId": "sg-012345","Issue": "Open SSH port"},
        environment="aws"
    )
    for step in playbook:
        print(step)
"""

import os
from jinja2 import Environment, FileSystemLoader, select_autoescape

# Initialize the Jinja2 environment (templates stored in 'templates/remediation/')
def load_templates(template_dir=None):
    template_dir = template_dir or os.path.join(os.path.dirname(__file__), '..', 'templates', 'remediation')
    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(['j2', 'jinja'])
    )
    return env

# Mock LLM enhancement function; in production, replace with an actual LLM API call
def mock_llm_enhance(text: str) -> str:
    # Simulate refining a step into a CLI command or IaC snippet
    if "sg-" in text:
        return f"aws ec2 revoke-security-group-ingress --group-id {text.split()[-1]} --protocol tcp --port 22 --cidr 0.0.0.0/0"
    if "role:read" in text:
        return "az role assignment delete --assignee <principal> --role Reader --scope /subscriptions/<sub>/resourceGroups/<rg>"
    # Default: return the original text with prefix
    return f"# TODO: {text}"

# Main function to generate a remediation playbook
def generate_playbook(control_id: str, findings: dict, environment: str = "aws") -> list:
    """
    Generate a remediation playbook for a specific control failure.

    Args:
        control_id: Identifier of the failed control (e.g., 'AC-2').
        findings: Contextual details from the drift detection or compliance scan.
            Example: { 'ResourceId': 'sg-012345', 'Issue': 'Open SSH port' }
        environment: Cloud environment ('aws', 'azure', or 'gcp').

    Returns:
        List of remediation steps as strings (CLI commands or code snippets).
    """
    env = load_templates()
    # Load the base template for this control
    try:
        template = env.get_template(f"{control_id}.j2")
    except Exception:
        # Fallback to a generic playbook template
        template = env.get_template("generic_playbook.j2")

    # Render the template with findings and environment context
    raw_steps = template.render(control=control_id, findings=findings, env=environment)
    # Split into individual steps (assume each line is one step)
    steps = [line.strip() for line in raw_steps.splitlines() if line.strip()]

    # Enhance each step via mock LLM
    enhanced_steps = [mock_llm_enhance(step) for step in steps]
    return enhanced_steps

# Example standalone execution
def run_example():
    playbook = generate_playbook(
        control_id="AC-2",
        findings={"ResourceId": "sg-012345", "Issue": "Open SSH port"},
        environment="aws"
    )
    print("Generated Remediation Playbook for AC-2:")
    for idx, step in enumerate(playbook, 1):
        print(f"Step {idx}: {step}")

if __name__ == "__main__":
    run_example()
