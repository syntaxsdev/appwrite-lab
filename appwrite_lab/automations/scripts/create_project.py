import asyncio
from playwright.async_api import Playwright, async_playwright
from ..common import AppwriteCLI
from ..utils import PlaywrightAutomationError
from ..models import AppwriteProjectCreation, AppwriteWebAuth
from ..functions import create_browser_context, login_to_console, cleanup_browser


async def create_project(playwright: Playwright) -> bool:
    """
    Create a project for the Appwrite lab.

    Args:
        playwright: Playwright instance.
    """
    acli = AppwriteCLI()
    auth = AppwriteWebAuth.from_env()
    vars = AppwriteProjectCreation.from_env()

    project_name = vars.project_name
    project_id = vars.project_id
    login_exc = acli.login(
        f"{auth.url}/v1",
        auth.admin_email,
        auth.admin_password,
    )
    get_project_exc = acli.get_project(project_id)

    login_res = login_exc.run()
    if login_res.returncode != 0:
        raise PlaywrightAutomationError(
            f"Failed to login to Appwrite: {login_res.stderr}"
        )

    proj_res = get_project_exc.run()
    if proj_res.returncode == 0:
        raise PlaywrightAutomationError(
            f"Project '{project_name}' with ID: '{project_id}' already exists"
        )

    else:
        browser, context = await create_browser_context(playwright, headless=True)
        page = await context.new_page()

        await login_to_console(page, auth.url, auth.admin_email, auth.admin_password)

        # Create project
        await page.get_by_role("button", name="Create project").click()
        await page.get_by_role("textbox", name="Name").fill(project_name)
        await page.get_by_role("button", name="Project ID").click()
        await page.get_by_role("textbox", name="Enter ID").fill(project_id)
        await page.get_by_role("button", name="Create", exact=True).click()

        await cleanup_browser(context, browser)
        print("Project created")


async def main():
    async with async_playwright() as playwright:
        return await create_project(playwright)


asyncio.run(main())
