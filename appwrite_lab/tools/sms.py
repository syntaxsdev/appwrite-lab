from appwrite_lab.models import Lab
from httpx import AsyncClient


class SMS:
    def __init__(self, lab: Lab):
        self.url = lab.sms_shim_url

    async def get_messages(self):
        async with AsyncClient(verify=False) as client:
            response = await client.get(f"{self.url}/inbox")
            return response.json().get("messages")

    async def clear_messages(self):
        async with AsyncClient(verify=False) as client:
            response = await client.post(f"{self.url}/clear")
            return response.json().get("ok")