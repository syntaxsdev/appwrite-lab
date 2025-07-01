from playwright.async_api import Playwright
from models import AppwriteUserCreation


async def create_user_and_api_key(
    playwright: Playwright, url: str, user: AppwriteUserCreation
) -> str:
    """
    Create a user and an API key for the Appwrite project.

    Args:
        playwright: Playwright instance.
        url: Appwrite URL.
        user: AppwriteUserCreation object.

    Returns:
        str: The API key.
    """
    browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context()
    page = await context.new_page()
    await page.goto(f"{url}/console/register")
    await page.wait_for_timeout(500)
    await page.get_by_role("textbox", name="Name").fill("Test")
    await page.get_by_role("textbox", name="Email").fill(user.admin_email)
    await page.get_by_role("textbox", name="Password").fill(user.admin_password)
    await page.get_by_role("button").nth(1).click()
    await page.get_by_role("button", name="Sign up").click()
    await page.wait_for_url("**/onboarding/create-project")

    await page.get_by_role("button", name="Project ID").click()
    await page.get_by_role("textbox", name="Enter ID").fill(user.project_id)
    await page.get_by_role("button", name="Create").click()
    await page.wait_for_url("**/get-started")

    await page.get_by_role("link", name="Overview").click()
    await page.get_by_role("tab", name="API keys").click()
    await page.get_by_role("link", name="Create API key", exact=True).click()
    await page.get_by_role("textbox", name="Name").fill("api_key")
    await page.get_by_label("", exact=True).click()
    await page.get_by_role("option", name="30 days").click()
    await page.get_by_role("button", name="Select all", exact=True).click()
    await page.get_by_role("button", name="Create").click()

    await page.get_by_role("button", name="Show text").click()
    api_key = await page.locator("span.code-text").text_content()

    # Cleanup
    await context.close()
    await browser.close()

    return api_key
