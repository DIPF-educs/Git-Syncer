# GIT Syncer
A small tool written in python3 that synchronizes a source and a fork git repository

Note: __Requires python 3__

## Synopsis
`python3 sync.py`

`usage: sync.py [-h] source fork [namespace]`


| parameter | description |
| ---- | ---- |
| source | The original git-url that was being forked from and was updated (should be synced) |
| fork | The forked repository url |
| namespace | a namespace (i.e. a folder) that is created in the fork (default: `source`) |
| --dry-run | doing a dry run |
| --file / -f | Loading a json to apply multiple repositories at once |

All branches and tags from the source are transferred to the fork and are stored in the folder given in `namespace`
* branches/tags will be generated using a folder structure using the namespace

## Configuration / URLs
To allow cloning and pushing to gitlab, a deploy key is required. For just cloning, a deploy token is sufficient.

The tool uses an `id_{rsa,ed25519,whatever}`-file in the working directory where it was called (if present).

Otherwise, provide a full url with credentials for cloning:
`https://gitlab+deploy-token-12:t67NCHtu3%fINVALDIG!!!FNOTWORKING"!!@gitlab.tba-hosting.de/MySkills/bke-sourceclone/tao-php-docker.git`

### JSON
Schema:
```json
{
    "$schema": "http://json-schema.org/draft-07/schema",
    "$id": "http://gitlab.tba-hosting.de/MySkills/Git-Sync.json",
    "type": "array",
    "title": "Git Sync Schema",
    "description": "A schema for specifing repos used for the Git-Sync tool.",
    "default": [],
    "additionalItems": true,
    "items": {
        "$id": "#/items",
        "type": "object",
        "title": "An configuration for syncing repositories",
        "default": {},
        "examples": [
            {
                "fork": "ssh://git@gitlab.tba-hosting.de:47478/MySkills/bke-sourceclone/TAO.git",
                "source": "https://gitlab.opit.hu/BKE/TAO.git",
                "id_rsa": "gitlab",
                "namespace": "tba21"
            }
        ],
        "additionalProperties": true,
        "required": [
            "source",
            "fork",
            "namespace"
        ],
        "properties": {
            "source": {
                "$id": "#/items/properties/source",
                "type": "string",
                "title": "Source Repository",
                "description": "Access URL for the original repository.",
                "default": "",
                "examples": [
                    "https://gitlab.opit.hu/BKE/TAO.git"
                ]
            },
            "fork": {
                "$id": "#/items/properties/fork",
                "type": "string",
                "title": "Forked Repository",
                "description": "Access URL for the forked repository.",
                "default": "",
                "examples": [
                    "ssh://git@gitlab.tba-hosting.de:47478/MySkills/bke-sourceclone/TAO.git"
                ]
            },
            "namespace": {
                "$id": "#/items/properties/namespace",
                "type": "string",
                "title": "Namespace",
                "description": "A generic prefix used for creating branches or tags.",
                "default": "",
                "examples": [
                    "tba21"
                ]
            },
            "ssh_file": {
                "$id": "#/items/properties/id_rsa",
                "type": "string",
                "title": "Private ssh_file file",
                "description": "An path to an private ssh id file",
                "default": "",
                "examples": [
                    "id_rsa"
                ]
            }
        }
    }
}
```
