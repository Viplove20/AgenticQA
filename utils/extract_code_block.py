import re

def extract_code_block(text: str) -> str:
    """Extract code from markdown code blocks if present."""
    match = re.search(r"```(?:typescript|javascript|ts|js)?\n(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()