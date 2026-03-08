def extract_typescript_code(text):

    if text is None:
        raise Exception("Agent response empty")

    # try fenced code first
    import re
    pattern = r"```(?:typescript|ts)?\s*([\s\S]*?)```"
    match = re.search(pattern, text)

    if match:
        return match.group(1).strip()

    # fallback: return raw text
    return text.strip()