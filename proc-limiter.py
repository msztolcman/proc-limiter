#!/usr/bin/env python3

import argparse
import hashlib
import pathlib
import shlex
import subprocess
import tempfile
import sys


__version__ = '0.1.0'


DB_NAME = 'proc-limiter'


def get_file_name(cmd):
    hash = hashlib.sha256(cmd).hexdigest()
    return hash


def count_descriptors(path):
    command = ['lsof', '-F', 'p', path]
    res = subprocess.Popen(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    res.wait()

    if res.returncode != 0:
        stderr = res.stderr.read().decode().strip()
        if stderr:
            print("lsof exit code is %d. Error:\n%s" % (res.returncode, stderr), file=sys.stderr)
            sys.exit(1)

    stdout = res.stdout.read().decode().strip()
    stdout = stdout.split("\n")
    return len(stdout)


def parse_args(args):
    p = argparse.ArgumentParser()
    p.add_argument('--limit', '-l', type=int, default=1, help='Max number of processes')
    p.add_argument('--command', '-c', type=str, help='Command to execute')
    # p.add_argument('--timeout', '-t', type=int, default=0, help='Timeout for single process')
    p.add_argument('--no-shell', default=False, action='store_true', help='Run command through shell')
    p.add_argument('--exit-code', type=int, default=1, help='Exit code on exceeded limit')

    args = p.parse_args(args)
    return args


def main():
    args = parse_args(sys.argv[1:])

    # if args.timeout <= 0:
    #     args.timeout = None

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

        proc = subprocess.Popen(command, shell=not args.no_shell)
        # proc.wait(timeout=args.timeout)
        proc.wait()

    sys.exit(proc.returncode)


if __name__ == '__main__':
    main()
