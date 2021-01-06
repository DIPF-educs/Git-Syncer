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

def print_start(msg):
    print(msg, end=" ", flush=True)
def print_done():
    print("✓")

def git(*args):
    global env, opts
    if opts.dry_run:
        print_done()
        print_start(f"Would call 'git {' '.join(args)}' ")
        res = type("Dummy", (object,), {})()
        res.stdout = b""
        return res
    return run(['git', *args], check=True, env=env, capture_output=True)

def create_tags_from_upstream(namespace):
    #filter only the tags from upstream
    spec = git("ls-remote","-t","upstream").stdout.decode().strip().splitlines()
    spec = [x.split()[1][len("refs/tags/"):] for x in spec]
    #filter tags with references, i.e ^{}
    spec = [x for x in spec if not "^{" in x]
    refspecs = [f"refs/tags/{tagname}:refs/tags/{namespace}/{tagname}" for tagname in spec]
    if(len(refspecs) == 0):
        print_start("No tags found -> skipping")
        print_done()
        return
    print_start(f"Pushing {len(refspecs)} tags")
    git("push","-f","origin",*refspecs)
    print_done()

def mirror(source, fork, namespace):
    curdir = os.getcwd()
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        print(f"Working in {os.getcwd()}")
        try:
            print_start(f"Cloning fork at ${fork}")
            git("clone", "--bare", fork, ".")
            print_done()
            print_start(f"Fetching source from {source}")
            git("remote", "add", "upstream", source)
            git('fetch', '--tags', 'upstream')
            print_done()
            print_start(f"Copy branches into namespace {namespace}")
            git("push", "-f", "origin", f"refs/remotes/upstream/*:refs/heads/{namespace}/*")
            print_done()
            create_tags_from_upstream(namespace)
        except Exception as e:
            print("Failed to invoke command", e)
            print(e.stdout)
            print(e.stderr)
            print(e.args)
        finally:
            os.chdir(curdir)
            print_start("Cleanup")
    print_done()

def set_id_rsa(path):
    if(os.path.exists(os.path.abspath(path))):
        env["GIT_SSH_COMMAND"] = f'ssh -i {os.path.abspath(path)} -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no'

def main():
    global env
    set_id_rsa(os.path.join(os.getcwd(),"id_rsa"))
    env["BASE_GIT_SSH_COMMAND"] = env.get("GIT_SSH_COMMAND", "")
    if opts.file != None and os.path.exists(opts.file):
        import json
        with open(opts.file, "r") as fp:
            repos = json.load(fp)
        filePath = os.path.dirname(opts.file)
        for repo in repos:
            if "ssh_file" in repo:
                ssh_file = os.path.join(filePath, repo['ssh_file'])
                print(f"Using own SSH Key {repo['ssh_file']} in {ssh_file}")
                os.chmod(ssh_file, 0o600)
                set_id_rsa(ssh_file)
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
