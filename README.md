# GIT Syncer
A small tool written in python3 that synchronizes a source and a fork git repository

Note: __Requires python 3__

## Synopsis
`python3 sync.py`

`usage: sync.py [-h] source fork [namespace]`
| ---- | ---- |
| source | The original git-url that was being forked from and was updated (should be synced) |
| fork | The forked repository url |
| namespace | a namespace (i.e. a folder) that is created in the fork (default: `source`) |

All branches from the source are transferred to the fork and are stored in the folder given in `namespace`

## Configuration / URLs
To allow cloning and pushing to gitlab, a deploy key is required. For just cloning, a deploy token is sufficient.

The tool uses an `id_rsa`-file in the working directory where it was called (if present).

Otherwise, provide a full url with credentials for cloning:
`https://gitlab+deploy-token-12:t67NCHtu3%fINVALDIG!!!FNOTWORKING"!!@gitlab.tba-hosting.de/MySkills/bke-sourceclone/tao-php-docker.git`
