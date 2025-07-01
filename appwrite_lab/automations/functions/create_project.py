import os
import asyncio
from playwright.async_api import Playwright, async_playwright
from automations.common import AppwriteCLI
from automations.utils import PlaywrightAutomationError


async def create_project(playwright: Playwright) -> bool:
    """
    Create a project for the Appwrite lab.

    Args:
        playwright: Playwright instance.
    """
    url = os.getenv("APPWRITE_URL")
    project_name = os.getenv("APPWRITE_PROJECT_NAME")
    project_id = os.getenv("APPWRITE_PROJECT_ID")
    admin_email = os.getenv("APPWRITE_ADMIN_EMAIL")
    admin_password = os.getenv("APPWRITE_ADMIN_PASSWORD")

    acli = AppwriteCLI()
    print(url, project_name, project_id, admin_email, admin_password)
    login_exc = acli.login(url, admin_email, admin_password)
    get_project_exc = acli.get_project(project_id)

    login_res = login_exc.run()
    if login_res.returncode != 0:
        raise PlaywrightAutomationError(
            f"Failed to login to Appwrite: {login_res.stderr}"
        )

    proj_res = get_project_exc.run()
    if proj_res.returncode == 0:
        return True

    browser = await playwright.chromium.launch(headless=True)
    context = await browser.new_context()
    page = await context.new_page()
    await page.goto(f"{url}/console/")
    # Login (abstract later)
    await page.get_by_role("textbox", name="Email").fill(admin_email)
    await page.get_by_role("textbox", name="Password").fill(admin_password)
    await page.get_by_role("button", name="Sign in").click()

    # Create project (abstract later)
    await page.get_by_role("button", name="Create project").click()
    await page.get_by_role("textbox", name="Name").fill(project_name)
    await page.get_by_role("button", name="Project ID").click()
    await page.get_by_role("textbox", name="Enter ID").fill(project_id)
    await page.get_by_role("button", name="Create", exact=True).click()

    # Cleanup
    await context.close()
    await browser.close()


async def main():
    async with async_playwright() as playwright:
        return await create_project(playwright)


asyncio.run(main())
