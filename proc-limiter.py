#!/usr/bin/env python  # -*- coding: utf-8 -*-

import hashlib
import pathlib
import shlex
import subprocess
import tempfile
import sys

import click
import sh

DB_NAME = 'proc-limiter'


def get_file_name(cmd):
    hash = hashlib.sha256(cmd).hexdigest()
    return hash


def count_descriptors(path):
    res = sh.lsof('-F', 'p', path).strip()
    res = res.split("\n")
    return len(res)

@click.command()
@click.option('--limit', type=int, default=1, help='Max number of processes')
@click.option('--command', type=str, help='Command to execute')
@click.option('--timeout', type=int, default=0, help='Timeout for single process')
@click.option('--no-shell', type=bool, default=False, help='Run command through shell')
@click.option('--exit-code', type=int, default=1, help='Exit code on exceeded limit')
def cli(command, limit=1, timeout=0, no_shell=False, exit_code=1):
    lock_file_name = get_file_name(str(command).encode())

    path = pathlib.Path(tempfile.gettempdir()) / DB_NAME
    if not path.exists():
        path.mkdir(0o700)
    lock_file_path = path / lock_file_name

    if no_shell:
        command = shlex.split(command)

    with open(str(lock_file_path), 'a+') as fh:
        cnt = count_descriptors(str(lock_file_path))
        
        if cnt >= limit:
            print('Limit of processes is exceeded, exiting', file=sys.stderr)
            sys.exit(exit_code)

        proc = subprocess.Popen(command, shell=True)
        proc.wait(None if timeout <= 0 else timeout)

    sys.exit(proc.returncode)

if __name__ == '__main__':
    cli()
