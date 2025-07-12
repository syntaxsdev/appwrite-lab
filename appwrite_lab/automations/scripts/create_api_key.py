import asyncio
import os
from playwright.async_api import Playwright, async_playwright
from ..functions import (
    create_browser_context,
    login_to_console,
    select_project_after_login,
    create_api_key_ui,
    cleanup_browser,
)
from ..utils import resultify, PlaywrightAutomationError
from ..models import AppwriteWebAuth, AppwriteAPIKeyCreation


async def create_api_key(playwright: Playwright) -> str:
    """
    Create an API key for the Appwrite project.

    Args:
        playwright: Playwright instance.
    """
    browser, context = await create_browser_context(playwright, headless=True)
    page = await context.new_page()

    auth = AppwriteWebAuth.from_env()
    api_key = AppwriteAPIKeyCreation.from_env()
    work_dir = os.getenv("HOME")
    await login_to_console(
        page=page,
        url=auth.url,
        admin_email=auth.admin_email,
        admin_password=auth.admin_password,
    )
    await select_project_after_login(page=page, project_name=api_key.project_name)
    key = await create_api_key_ui(
        page=page,
        key_name=api_key.key_name,
        key_expiry=api_key.key_expiry,
    )
    await cleanup_browser(context, browser)

    if not key:
        raise PlaywrightAutomationError("Failed to create API key")

    resultify(work_dir, key)


async def main():
    async with async_playwright() as playwright:
        return await create_api_key(playwright)


asyncio.run(main())
