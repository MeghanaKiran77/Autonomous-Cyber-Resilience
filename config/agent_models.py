"""
Agent-specific model configurations.

Based on 2026 Groq benchmarks, optimized for:
- Researcher: Deep reasoning for vulnerability analysis
- Attacker: Fast, creative exploit generation
- Fixer: Code-heavy patching with best practices
"""

from dataclasses import dataclass


@dataclass
class AgentModelConfig:
    """Model configuration for a specific agent role."""

    provider: str
    model: str
    temperature: float
    max_tokens: int
    reasoning: str  # Why this model was chosen


# Researcher Agent: Deep reasoning for vulnerability discovery
RESEARCHER_MODEL = AgentModelConfig(
    provider="groq",
    model="llama-3.3-70b-versatile",  # Updated: qwen-qwq-32b decommissioned
    temperature=0.3,  # Lower for more focused analysis
    max_tokens=2048,
    reasoning=(
        "llama-3.3-70b-versatile provides excellent reasoning capabilities. "
        "Large 70B parameter model for deep analysis of complex vulnerabilities. "
        "Versatile across different vulnerability types (SQLi, IDOR, XSS)."
    ),
)

# Attacker Agent: Fast, creative exploit generation
ATTACKER_MODEL = AgentModelConfig(
    provider="groq",
    model="llama-3.3-70b-versatile",  # Fallback: llama-4-scout not available on Groq
    temperature=0.5,  # Moderate for creative but precise exploits
    max_tokens=1024,
    reasoning=(
        "llama-3.3-70b-versatile provides excellent reasoning and creativity. "
        "Large 70B parameter model for generating precise exploit payloads. "
        "Proven to work well on Groq's infrastructure."
    ),
)

# Fixer Agent: Code-heavy patching with best practices
FIXER_MODEL = AgentModelConfig(
    provider="groq",
    model="llama-3.3-70b-versatile",  # Fallback: gpt-oss-120b not available on Groq
    temperature=0.2,  # Very low for deterministic, safe patches
    max_tokens=2048,
    reasoning=(
        "llama-3.3-70b-versatile provides good code generation capabilities. "
        "Large 70B parameter model for generating secure patches. "
        "Low temperature ensures deterministic, safe patch generation."
    ),
)


def get_agent_model(agent_name: str) -> AgentModelConfig:
    """
    Get optimal model configuration for an agent.

    Args:
        agent_name: Agent name (researcher, attacker, fixer).

    Returns:
        AgentModelConfig for the specified agent.

    Raises:
        ValueError: If agent_name is not recognized.
    """
    models = {
        "researcher": RESEARCHER_MODEL,
        "attacker": ATTACKER_MODEL,
        "fixer": FIXER_MODEL,
    }

    agent_name_lower = agent_name.lower()
    if agent_name_lower not in models:
        raise ValueError(
            f"Unknown agent: {agent_name}. "
            f"Supported: {list(models.keys())}"
        )

    return models[agent_name_lower]
