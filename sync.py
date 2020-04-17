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
    return run(['git', *args], check=True, env=env, capture_output=True)

def create_tags_from_upstream(namespace):
    global env
    spec = git("ls-remote","-t","upstream").stdout.decode().strip().splitlines()
    spec = [x.split()[1][len("refs/tags/"):] for x in spec]
    refspecs = [f"refs/tags/{tagname}:refs/tags/{namespace}/{tagname}" for tagname in spec]
    print(f"Pushing {len(refspecs)} tags ", end="")
    #git("push","-f","origin",*refspecs)
    run(["git","push","-f","origin", *refspecs], env=env, check=True, capture_output=True)
    print("✓")

def mirror(source, fork, namespace):
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
            res = git('fetch', '--tags', 'upstream')
            print(res.stderr)
            print("✓")
            print("Copy branches ", end="")
            #git("push", "-f", "origin", f"refs/remotes/upstream/*:refs/heads/{namespace}/*")
            print("✓")
            create_tags_from_upstream(namespace)
        except Exception as e:
            print("Failed to invoke command", e)
            print(e.stdout)
            print(e.stderr)
            print(e.args)
        finally:
            os.chdir(curdir)
            print("Cleanup ", end="")
    print("✓")

def set_id_rsa(path):
    if(os.path.exists(os.path.abspath(path))):
        env["GIT_SSH_COMMAND"] = f'ssh -i {os.path.abspath(path)} -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no'

def main():
    global env
    set_id_rsa(os.path.join(os.getcwd(),"id_rsa"))
    env["BASE_GIT_SSH_COMMAND"] = env.get("GIT_SSH_COMMAND", "")
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