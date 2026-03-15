from pathlib import Path


def load_prompt(filename: str) -> str:
    prompt_path = Path("prompts") / filename
    if prompt_path.exists():
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    return f"You are a {filename.replace('.md', '')} agent."