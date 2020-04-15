#!/usr/bin/env python3
from argparse import ArgumentParser
from subprocess import run
import shutil
import os
import tempfile

args = ArgumentParser()
args.add_argument("source")
args.add_argument("fork")
args.add_argument("namespace", default="source", nargs="?")
opts = args.parse_args()

env = {}

def git(*args):
    global env
    return run(['git'] + list(args), check=True, env=env, capture_output=True)

if(os.path.exists("id_rsa")):
    env["GIT_SSH_COMMAND"] = f'ssh -i {os.getcwd()}/id_rsa -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no'


skipped = 0
with tempfile.TemporaryDirectory() as tmpdir:
    os.chdir(tmpdir)
    print(f"Working in {os.getcwd()}")
    try:
        print("Cloning fork ", end="")
        git("clone", "--bare", opts.fork, ".")
        print("✓")
        print("Fetching source ", end="")
        git("remote", "add", "upstream", opts.source)
        git('fetch', 'upstream')
        print("✓")
        print("Copy branches", end="")
        git("push", "-f", "origin", f"refs/remotes/upstream/*:refs/heads/{opts.namespace}/*")
        print("✓")
        tags = git("tag", "-l").stdout.decode().split()
        for t in tags:
            #avoid nesting (shouldnt happen)
            #and additional pushing of tags if they are already present
            if(t.startswith(opts.namespace)):
                skipped += 1
                #print(f"Skipping already namespaced tag {t}")
                continue
            if(f"{opts.namespace}/{t}" in tags):
                #print(f"Skipping {t} as it is already present")
                skipped += 1
                continue
            print(f"Pushing tag {t}", end="")
            git("push", "-f", "origin", f"refs/tags/{t}:refs/tags/{opts.namespace}/{t}")
            print("✓")
    except Exception as e:
        print("Failed to invoke command", e)
        print(e.stdout)
        print(e.stderr)
        print(e.args)
    print("Cleanup ", end="")
print("✓")
print(f"Skipped {skipped} tags")