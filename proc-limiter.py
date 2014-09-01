#!/usr/bin/env python  # -*- coding: utf-8 -*-

import argparse
import hashlib
import pathlib
import shlex
import subprocess
import tempfile
import sys

# import click
import sh

DB_NAME = 'proc-limiter'


def get_file_name(cmd):
    hash = hashlib.sha256(cmd).hexdigest()
    return hash


def count_descriptors(path):
    res = sh.lsof('-F', 'p', path).strip()
    res = res.split("\n")
    return len(res)


def cli(args):
    # command, limit = 1, timeout = 0, no_shell = False, exit_code = 1 =
    lock_file_name = get_file_name(str(args.command).encode())

    path = pathlib.Path(tempfile.gettempdir()) / DB_NAME
    if not path.exists():
        path.mkdir(0o700)
    lock_file_path = path / lock_file_name

    if args.no_shell:
        command = shlex.split(args.command)
    else:
        command = args.command

    with open(str(lock_file_path), 'a+'):
        cnt = count_descriptors(str(lock_file_path))
        if (cnt - 1) >= args.limit:  # minus current process
            print('Limit of processes is exceeded, exiting', file=sys.stderr)
            sys.exit(args.exit_code)

        proc = subprocess.Popen(command, shell=True)
        # proc.wait(timeout=args.timeout)
        proc.wait()

    sys.exit(proc.returncode)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--limit', '-l', type=int, default=1, help='Max number of processes')
    p.add_argument('--command', '-c', type=str, help='Command to execute')
    p.add_argument('--timeout', '-t', type=int, default=0, help='Timeout for single process')
    p.add_argument('--no-shell', type=bool, default=False, help='Run command through shell')
    p.add_argument('--exit-code', type=int, default=1, help='Exit code on exceeded limit')

    args = p.parse_args()

    if args.timeout <= 0:
        args.timeout = None

    return cli(args)

if __name__ == '__main__':
    main()
