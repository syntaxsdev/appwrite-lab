import asyncio
from playwright.async_api import Playwright, async_playwright
from automations.common import AppwriteCLI
from automations.utils import PlaywrightAutomationError
from automations.models import AppwriteSyncProject, AppwriteWebAuth


async def sync_project(playwright: Playwright) -> bool:
    """
    Create a project for the Appwrite lab.

    Args:
        playwright: Playwright instance.
    """
    acli = AppwriteCLI()
    auth = AppwriteWebAuth.from_env()
    sync = AppwriteSyncProject.from_env()
    resource = sync.resource
    login_exc = acli.login(
        f"{auth.url}/v1",
        auth.admin_email,
        auth.admin_password,
    )
    login_res = login_exc.run()
    if login_res.returncode != 0:
        raise PlaywrightAutomationError(
            f"Failed to login to Appwrite: {login_res.stderr}"
        )

    sync_res = acli.sync_project(resource).run()
    if sync_res.returncode != 0:
        raise PlaywrightAutomationError(f"Failed to sync project: {sync_res.stderr}")
    print("Project synced")


async def main():
    async with async_playwright() as playwright:
        return await sync_project(playwright)


asyncio.run(main())
