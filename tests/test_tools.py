import pytest
from appwrite_lab.tools.sms import SMS
from appwrite_lab.models import Lab
from httpx import AsyncClient
import asyncio

@pytest.mark.e2e
@pytest.mark.asyncio
async def test_sms_get_messages(sms: SMS, lab: Lab):
    await sms.clear_messages()
    messages = await sms.get_messages()
    assert len(messages) == 0

    async with AsyncClient(verify=False) as client:
        response = await client.post(
            f"{lab.url}/v1/account/sessions/phone",
            json={"userId": "unique()", "phone": "+15555550123"},
            headers={"X-Appwrite-Project": lab.projects.get("default").project_id},
        )
        assert response.status_code == 201
    await asyncio.sleep(1)
    messages = await sms.get_messages()
    assert len(messages) == 1
    assert messages[0].get("frm") == "+15555555555"
    assert len(messages[0].get("body")) == 6


