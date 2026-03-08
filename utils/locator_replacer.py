from utils.locator_parser import extract_locators
from memory.locator_memory import search_locator_fix


def apply_memory_fixes(playwright_code):

    locators = extract_locators(playwright_code)

    updated_code = playwright_code

    for locator in locators:

        fix = search_locator_fix(locator)

        if fix:
            updated_code = updated_code.replace(locator, fix)

    return updated_code