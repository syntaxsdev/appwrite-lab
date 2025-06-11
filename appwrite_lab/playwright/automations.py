from playwright.async_api import Playwright, async_playwright
from models import AppwriteUserCreation
from functions import create_user_and_api_key
from appwrite_lab._orchestrator import ServiceOrchestrator

class AppwriteAutomation:
    def __init__(self, orchestrator: ServiceOrchestrator):
        self.orchestrator = orchestrator
        self.playwright = async_playwright()

    async def automate_fetch_api_key(
        self, config: AppwriteUserCreation | None = None
    ) -> tuple[str, AppwriteUserCreation]:
        """Create a user and an API key for the Appwrite project.

        Args:
            config: AppwriteUserCreation object.
                If None, a random user and project will be created

        Returns:
            tuple[str, AppwriteUserCreation]: The API key and the user configuration
        """
        if not config:
            config = AppwriteUserCreation().generate()
        api_key = await create_user_and_api_key(self.playwright, self.url, config)
        return api_key, config
