# appwrite-lab
Zero-click Appwrite test environments

## Installation
```sh
pip install appwrite-lab
```
## Appwrite Lab features (coming)
- [x] Spin up ephemeral Appwrite instances with Docker/Podman
- [x] Automatically grab API keys (for programmatic access)
- [ ] Test suite
- [ ] Environment syncing
- [ ] Appwrite data population
- [x] Clean teardowns


## CLI Usage
### Help with appwrite-lab CLI
```sh
appwrite-lab --help
```

To get started spinning up a lab instance, use:

```sh
appwrite-lab new lab test-lab --version 1.7.4
```

To teardown,

```sh
appwrite-lab stop test-lab
```
