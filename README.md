# appwrite-lab
Zero-click Appwrite test environments

## Installation
```sh
pip install appwrite-lab
```
## Appwrite Lab features (coming)
1. Spin up ephemeral Appwrite instances with Docker/Podman
2. Automatically grab API keys (for programmatic access)
3. Test suite
4. Environment syncing
5. Appwrite data population
6. Clean teardowns


## CLI Usage
### Help with appwrite-lab CLI
```sh
appwrite-lab --help
```

To get started spinning up a lab instance, use:

```sh
appwrite-lab new lab --name test-lab --version 1.7.4
```

To teardown,

```sh
appwrite-lab stop test-lab
```
