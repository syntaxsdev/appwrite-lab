# appwrite-lab
Zero-click Appwrite test environments.

Allows you to spin up versioned Appwrite deployments for easy testing via CLI or through code, that can be ran in a sequence of E2E tests.

## Installation
```sh
pip install appwrite-lab
```
## Appwrite Lab features
- [x] Spin up ephemeral Appwrite instances with Docker/Podman
- [x] Automatically grab API keys (for programmatic access)
- [x] Environment syncing (with `appwrite.json`)
- [x] Clean teardowns
- [x] Test suite

## Appwrite Lab (in progress)
- [ ] Appwrite data population

## CLI Usage
### Help with appwrite-lab CLI
```sh
appwrite-lab --help
```
or
```sh
awlab --help
```

### To get started spinning up a lab instance, use:

```sh
awlab new lab test --version 1.7.4
```
*Note:* This might take a few minutes the first time as its downloading all of the necessary images to launch Appwrite.
#### Example of additional args:
Additional arguments can be found here.
```sh
awlab new lab --help
```

```sh
awlab new lab test --version 1.7.4 --port 8005 --email test@example.com --password xxxxxxx12
```

### To teardown

```sh
awlab stop test
```
### Listing Appwrite Labs
```sh
awlab list labs
```
<img width="673" height="79" alt="image" src="https://github.com/user-attachments/assets/566bb734-8684-4b5b-ae34-70eac04af812" />

### Sync an Appwrite lab from your prod lab schema
Run in the same folder where your `appwrite.json` is located to sync `all` resources:
```sh
awlab sync test
```
or sync a specific resource:

```sh
awlab sync test --resource functions
```

## Python usage

### Creating a lab
```py
from appwrite_lab import Labs
from appwrite_lab.automations.models import AppwriteLabCreation

labs = Labs()
lab_res = labs.new(
    name="test",
    version="1.7.4",
    auth=AppwriteLabCreation(
        admin_email="test@example.com",
        admin_password="xxxxxxx12",
        project_id=None, # for auto gen
        project_name=None, # for auto gen
    )
    port=8005
)

assert lab_res.data
```

#### Random generation that's compliant
```py
from appwrite_lab.models import AppwriteLabCreation

auth = AppwriteLabCreation.generate()
```

### Syncing a lab
```py
from appwrite_lab import Labs
from appwrite_lab.automations.models import Expiration

Labs().sync_with_appwrite_config(
    name="test",
    appwrite_json="appwrite.json", # if not directly in folder
    sync_type="all",
    expiration=Expiration.THIRTY_DAYS,
)
```
## Known Troubleshooting
### Podman support and Selinux
Since I am mimicking the `compose` file that Appwrite provides, it was not designed to work rootless, but I have adjusted to work also on Fedora. You will need to turn `selinux` off for now to use.


