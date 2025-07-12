from playwright.async_api import Playwright, Page, BrowserContext, Browser


async def create_browser_context(playwright: Playwright, headless: bool = True):
    """Create a browser context for automation."""
    browser = await playwright.chromium.launch(headless=headless)
    context = await browser.new_context()
    return browser, context


async def login_to_console(page: Page, url: str, admin_email: str, admin_password: str):
    """Login to the Appwrite console."""
    await page.goto(f"{url}/console/")
    await page.get_by_role("textbox", name="Email").fill(admin_email)
    await page.get_by_role("textbox", name="Password").fill(admin_password)
    await page.get_by_role("button", name="Sign in").click()


async def select_project_after_login(page: Page, project_name: str):
    """Select a project after the login screen."""
    await page.get_by_role("link", name=f"No apps {project_name}").click()


async def register_user(page: Page, url: str, admin_email: str, admin_password: str):
    """Register a new user in Appwrite."""
    await page.goto(f"{url}/console/register")
    await page.wait_for_timeout(100)
    await page.get_by_role("textbox", name="Name").fill("Test User")
    await page.get_by_role("textbox", name="Email").fill(admin_email)
    await page.get_by_role("textbox", name="Password").fill(admin_password)
    await page.get_by_role("button").nth(1).click()
    await page.get_by_role("button", name="Sign up").click()
    await page.wait_for_url("**/onboarding/create-project")


async def create_project_ui(
    page: Page, project_id: str | None, project_name: str = None
):
    """Create a project through the UI."""
    if project_name:
        await page.get_by_role("textbox", name="Project name").fill(project_name)
    await page.get_by_role("button", name="Project ID").click()
    await page.get_by_role("textbox", name="Enter ID").fill(project_id)
    await page.get_by_role("button", name="Create").click()


async def create_api_key_ui(
    page: Page, key_name: str = "api_key", key_expiry: str = "30 days"
) -> str:
    """Create an API key through the UI."""
    await page.wait_for_timeout(500)
    await page.get_by_role("link", name="Overview").click()
    await page.get_by_role("tab", name="API keys").click()
    await page.get_by_role("link", name="Create API key", exact=True).click()
    await page.get_by_role("textbox", name="Name").fill(key_name)
    await page.get_by_label("", exact=True).click()
    await page.get_by_role("option", name=key_expiry).click()
    await page.get_by_role("button", name="Select all", exact=True).click()
    await page.get_by_role("button", name="Create").click()

    await page.locator(".interactiveTextContainer.svelte-numtrf").hover()
    await page.get_by_role("button", name="Show text").click()
    return await page.locator("span.code-text").text_content()


async def cleanup_browser(context: BrowserContext, browser: Browser):
    """Clean up browser resources."""
    await context.close()
    await browser.close()
