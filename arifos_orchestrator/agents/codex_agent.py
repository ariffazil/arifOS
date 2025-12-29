"""
Codex Agent: Code Generation Layer

Responsibilities:
- Generate production-ready code grounded in Claude's truth layer
- Enforce error handling and type hints
- Add governance audit comments
- Output clean, executable code

Model: gpt-4o
"""

import os
from typing import Dict, Optional
from openai import OpenAI


class CodexAgent:
    """
    Code generation agent powered by ChatGPT

    Takes Claude's constitutional truth as foundation,
    generates production code with governance constraints.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Codex agent

        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key required. "
                "Set OPENAI_API_KEY environment variable or pass api_key parameter."
            )

        self.client = OpenAI(api_key=self.api_key)
        self.model = "gpt-4o"

    def generate_code(self, spec: str, claude_truth: str, language: str = "python") -> Dict:
        """
        Generate code grounded in Claude's truth layer

        Args:
            spec: Code specification/requirements
            claude_truth: Claude's constitutional analysis
            language: Target language (default: python)

        Returns:
            dict: Generated code with metadata
        """
        prompt = f"""
Claude's truth foundation (Constitutional reasoning):
{claude_truth}
________________________________________

Generate production-ready {language} code for:
{spec}

Requirements:
1. Type hints ({language} / TypeScript equivalent)
2. Error handling (no silent failures)
3. Logging (trace entropy reduction if applicable)
4. Governance audit comment at top

Code format:
```{language}
# Governance Audit: [Brief statement of what this code does and why it's safe]
# Generated: [Current date]
# Grounded in: Claude truth layer (Floors 1-2)

[Your code here]
```

IMPORTANT:
- No hardcoded credentials
- No irreversible operations without confirmation
- Error handling for edge cases
- Clean, readable, maintainable code
"""

        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0.7,
            messages=[
                {
                    "role": "system",
                    "content": "You are arifOS Codex: generate code grounded in thermodynamic principles and constitutional governance.",
                },
                {"role": "user", "content": prompt},
            ],
        )

        generated_code = response.choices[0].message.content

        return {
            "code": generated_code,
            "language": language,
            "model": self.model,
            "grounded_in": "Claude truth layer (Floors 1-2)",
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            },
        }

    def refine_code(self, code: str, feedback: str) -> Dict:
        """
        Refine existing code based on feedback

        Args:
            code: Existing code to refine
            feedback: Refinement instructions

        Returns:
            dict: Refined code with metadata
        """
        prompt = f"""
Refine this code based on feedback:

Original code:
```
{code}
```

Feedback:
{feedback}

Provide improved version maintaining:
- Type hints
- Error handling
- Governance audit comment
"""

        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0.5,  # Lower temperature for refinement
            messages=[
                {
                    "role": "system",
                    "content": "You refine code under arifOS constitutional constraints.",
                },
                {"role": "user", "content": prompt},
            ],
        )

        refined_code = response.choices[0].message.content

        return {
            "code": refined_code,
            "model": self.model,
            "refinement": "Applied feedback while maintaining governance constraints",
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            },
        }
