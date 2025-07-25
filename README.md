# appwrite-lab
Zero-click Appwrite test environments.

Allows you to spin up versioned Appwrite deployments for easy testing via CLI of through code, that can be ran in a sequence of E2E tests.

## Installation
```sh
pip install appwrite-lab
```
## Appwrite Lab features (in progress)
- [x] Spin up ephemeral Appwrite instances with Docker/Podman
- [x] Automatically grab API keys (for programmatic access)
- [x] Environment syncing
- [x] Clean teardowns

## Appwrite Lab in progress features
- [ ] Test suite
- [ ] Appwrite data population

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

### Sync an Appwrite lab from your prod lab schema
Run in the same folder where your `appwrite.json` is located to sync `all` resources:
```sh
appwrite-lab sync test-lab
```
or sync a specific resource:

```sh
appwrite-lab sync test-lab --resource functions
```

## Known Troubleshooting
### Podman support and Selinux
Since I am mimicking the `compose` file that Appwrite provides, it was not designed to work rootless, but I have adjusted to work also on Fedora. You will need to turn `selinux` off for now to use.


