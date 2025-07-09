import os
import asyncio
from playwright.async_api import Playwright, async_playwright
from ..functions import (
    create_browser_context,
    register_user,
    create_project_ui,
    create_api_key_ui,
    cleanup_browser,
)
from ..utils import resultify
from ..models import AppwriteAPIKeyCreation, AppwriteUserCreation


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
    auth = AppwriteUserCreation.from_env()
    api_key_env = AppwriteAPIKeyCreation.from_env()
    work_dir = os.getenv("HOME")

    browser, context = await create_browser_context(playwright, headless=True)
    page = await context.new_page()

    await register_user(
        page=page,
        url=auth.url,
        admin_email=auth.admin_email,
        admin_password=auth.admin_password,
    )
    api_key = await create_api_key_ui(
        page=page, key_name=api_key_env.key_name, key_expiry=api_key_env.key_expiry
    )
    await cleanup_browser(context, browser)

    resultify(work_dir, api_key)


async def main():
    async with async_playwright() as playwright:
        return await create_user_and_api_key(playwright)


asyncio.run(main())
