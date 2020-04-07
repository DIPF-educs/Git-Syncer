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


with tempfile.TemporaryDirectory() as tmpdir:
    os.chdir(tmpdir)
    print(f"Currently in {os.getcwd()}")

    try:
        print("Cloning fork ", end="")
        git("clone", "--bare", opts.fork, ".")
        print("✓")
        print("Fetching source ", end="")
        git("remote", "add", "upstream", opts.source)
        git('fetch', 'upstream')
        print("✓")
        branches = git("branch", "-a")
        for br in branches.stdout.decode().split():
            if(not br.startswith('remotes/upstream')):
                continue
            br = br[len("remotes/upstream/"):] 
            print(f"Pushing branch {br}", end="")
            git("push", "-f", "origin", f"refs/remotes/upstream/{br}:refs/heads/{opts.namespace}/{br}")
            print("✓")
    except Exception as e:
        print("Failed to invoke command", e)
        print(e.stdout)
        print(e.stderr)
        print(e.args)
    print("Would Cleanup ", end="")
print("✓")
