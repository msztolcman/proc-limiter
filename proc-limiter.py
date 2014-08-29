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

@click.command()
@click.option('--limit', type=int, default=1, help='Max number of processes')
@click.option('--command', type=str, help='Command to execute')
@click.option('--timeout', type=int, default=0, help='Timeout for single process')
@click.option('--no-shell', type=bool, default=False, help='Run command through shell')
def cli(command, limit=1, timeout=0, no_shell=False):
    lock_file_name = get_file_name(str(command).encode())

    path = pathlib.Path(tempfile.gettempdir()) / DB_NAME
    if not path.exists():
        path.mkdir(0o700)
    lock_file_path = path / lock_file_name

    if no_shell:
        command = shlex.split(command)


    with open(str(lock_file_path), 'a+') as fh:
        print('command', command)
        print('path', lock_file_path)
        print('lsof', sh.lsof(str(lock_file_path).encode()))
        sys.exit()

        proc = subprocess.Popen(command, shell=True)
        proc.wait(None if timeout <= 0 else timeout)

    sys.exit(proc.returncode)

if __name__ == '__main__':
    cli()
