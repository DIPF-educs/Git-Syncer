#!/usr/bin/env python3
from argparse import ArgumentParser
from subprocess import run
import shutil
import os
import tempfile

args = ArgumentParser()
args.add_argument("-f", "--file", nargs="?")
args.add_argument("--dry-run", action="store_true")
args.add_argument("source", nargs="?")
args.add_argument("fork", nargs="?")
args.add_argument("namespace", default="source", nargs="?")
opts = args.parse_args()

env = {}

def git(*args):
    global env, opts
    if opts.dry_run:
        print(f"Would call 'git {' '.join(args)}'  ", end="")
        res = type("Dummy", (object,), {})()
        res.stdout = b""
        return res
    return run(['git'] + list(args), check=True, env=env, capture_output=True)


def mirror(source, fork, namespace):
    skipped = 0
    curdir = os.getcwd()
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        print(f"Working in {os.getcwd()}")
        try:
            print("Cloning fork ", end="")
            git("clone", "--bare", fork, ".")
            print("✓")
            print("Fetching source ", end="")
            git("remote", "add", "upstream", source)
            git('fetch', 'upstream')
            print("✓")
            print("Copy branches ", end="")
            git("push", "-f", "origin", f"refs/remotes/upstream/*:refs/heads/{namespace}/*")
            print("✓")
            tags = git("tag", "-l").stdout.decode().split()
            for t in tags:
                #avoid nesting (shouldnt happen)
                #and additional pushing of tags if they are already present
                if(t.startswith(namespace)):
                    skipped += 1
                    #print(f"Skipping already namespaced tag {t}")
                    continue
                if(f"{namespace}/{t}" in tags):
                    #print(f"Skipping {t} as it is already present")
                    skipped += 1
                    continue
                print(f"Pushing tag {t} ", end="")
                git("push", "-f", "origin", f"refs/tags/{t}:refs/tags/{namespace}/{t}")
                print("✓")
        except Exception as e:
            print("Failed to invoke command", e)
            print(e.stdout)
            print(e.stderr)
            print(e.args)
        finally:
            os.chdir(curdir)
            print("Cleanup ", end="")
    print("✓")
    print(f"Skipped {skipped} tags")

def set_id_rsa(path):
    if(os.path.exists(os.path.abspath(path))):
        env["GIT_SSH_COMMAND"] = f'ssh -i {os.path.abspath(path)} -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no'

def main():
    global env
    set_id_rsa(os.path.join(os.getcwd(),"id_rsa"))
    env["BASE_GIT_SSH_COMMAND"] = env.get("GIT_SSH_COMMAND", "")
    skipped = 0
    if opts.file != None and os.path.exists(opts.file):
        import json
        with open(opts.file) as fp:
            repos = json.load(fp)
        filePath = os.path.dirname(opts.file)
        for repo in repos:
            if "ssh_file" in repo:
                print(f"Using own SSH Key {repo['ssh_file']}")
                set_id_rsa(os.path.join(filePath, repo['ssh_file']))
            mirror(repo["source"], repo["fork"], repo["namespace"])
            #restore
            if "ssh_file" in repo:
                env["GIT_SSH_COMMAND"] = env["BASE_GIT_SSH_COMMAND"]

    else:
        if not opts.source or not opts.fork:
            args.print_usage()
            exit(1)
        mirror(opts.source, opts.fork, opts.namespace)

if __name__ == "__main__":
    main()