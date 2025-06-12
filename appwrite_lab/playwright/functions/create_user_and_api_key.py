import os
import asyncio
from playwright.async_api import Playwright, async_playwright


async def create_user_and_api_key(playwright: Playwright) -> str:
    """
    Create a user and an API key for the Appwrite project.

    Args:
        playwright: Playwright instance.
        url: Appwrite URL.
        user: AppwriteUserCreation object.

    Returns:
        str: The API key.
    """

    url = os.getenv("APPWRITE_URL")
    project_id = os.getenv("APPWRITE_PROJECT_ID")
    admin_email = os.getenv("APPWRITE_ADMIN_EMAIL")
    admin_password = os.getenv("APPWRITE_ADMIN_PASSWORD")

    browser = await playwright.chromium.launch(headless=True)
    context = await browser.new_context()
    page = await context.new_page()
    await page.goto(f"{url}/console/register")
    await page.wait_for_timeout(500)
    await page.get_by_role("textbox", name="Name").fill("Test")
    await page.get_by_role("textbox", name="Email").fill(admin_email)
    await page.get_by_role("textbox", name="Password").fill(admin_password)
    await page.get_by_role("button").nth(1).click()
    await page.get_by_role("button", name="Sign up").click()
    await page.wait_for_url("**/onboarding/create-project")

    await page.get_by_role("button", name="Project ID").click()
    await page.get_by_role("textbox", name="Enter ID").fill(project_id)
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

    await page.locator(".interactiveTextContainer.svelte-numtrf").hover()
    await page.get_by_role("button", name="Show text").click()
    api_key = await page.locator("span.code-text").text_content()
    # Cleanup
    await context.close()
    await browser.close()

    try:
        with open("/playwright/result.txt", "w") as f:
            f.write(api_key)
    except Exception as e:
        print("ERROR", e)


async def main():
    async with async_playwright() as playwright:
        return await create_user_and_api_key(playwright)


asyncio.run(main())
