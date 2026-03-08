import re

def extract_locators(playwright_code: str):

    patterns = [
        r'locator\("([^"]+)"\)',
        r"locator\('([^']+)'\)",
        r'getByText\("([^"]+)"\)',
        r"getByText\('([^']+)'\)",
        r'getByTestId\("([^"]+)"\)',
        r"getByTestId\('([^']+)'\)",
        r'getByLabel\("([^"]+)"\)',
        r"getByLabel\('([^']+)'\)",
        r'getByPlaceholder\("([^"]+)"\)',
        r"getByPlaceholder\('([^']+)'\)"
    ]

    locators = []

    for pattern in patterns:
        matches = re.findall(pattern, playwright_code)
        locators.extend(matches)

    return list(set(locators))