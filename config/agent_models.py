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
    model="qwen-qwq-32b",  # or "qwen-3-32b"
    temperature=0.3,  # Lower for more focused analysis
    max_tokens=2048,
    reasoning=(
        "qwen-qwq-32b excels at deep reasoning with <think> tokens. "
        "Rivals DeepSeek-R1 and o1-mini for finding obscure zero-day logic flaws. "
        "Uses RL reasoning to analyze complex application-layer vulnerabilities."
    ),
)

# Attacker Agent: Fast, creative exploit generation
ATTACKER_MODEL = AgentModelConfig(
    provider="groq",
    model="llama-4-scout-17b-16e-instruct",
    temperature=0.5,  # Moderate for creative but precise exploits
    max_tokens=1024,
    reasoning=(
        "llama-4-scout is a MoE model with excellent steerability. "
        "Supports parallel tool use for testing multiple attack vectors. "
        "Fast and efficient for generating precise exploit payloads (SQL, XSS, etc.)."
    ),
)

# Fixer Agent: Code-heavy patching with best practices
FIXER_MODEL = AgentModelConfig(
    provider="groq",
    model="gpt-oss-120b",  # or "gpt-oss-20b" for speed
    temperature=0.2,  # Very low for deterministic, safe patches
    max_tokens=2048,
    reasoning=(
        "gpt-oss-120b has massive knowledge base of software engineering patterns. "
        "MoE architecture makes it faster than dense models while maintaining accuracy. "
        "Fine-tuned on high-quality code repositories for verified patching."
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
