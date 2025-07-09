import os
import asyncio
from playwright.async_api import Playwright, async_playwright
from ..functions import create_browser_context, register_user, create_project_ui, create_api_key_ui, cleanup_browser


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
    work_dir = os.getenv("HOME")

    browser, context = await create_browser_context(playwright, headless=True)
    page = await context.new_page()
    
    await register_user(page, url, admin_email, admin_password)
    await create_project_ui(page, project_id)
    await page.wait_for_url("**/get-started")
    
    api_key = await create_api_key_ui(page)
    await cleanup_browser(context, browser)

    try:
        with open(f"{work_dir}/result.txt", "w") as f:
            f.write(api_key)
    except Exception as e:
        print("ERROR", e)


async def main():
    async with async_playwright() as playwright:
        return await create_user_and_api_key(playwright)


asyncio.run(main())
