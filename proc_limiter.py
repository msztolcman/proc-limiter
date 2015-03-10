#!/usr/bin/env python3

import argparse
import hashlib
import os
import pathlib
import shlex
import stat
import subprocess
import tempfile
import sys


__version__ = '0.3.1'


DB_NAME = 'proc-limiter'
DEBUG = False


def debug(name, *a):
    if not DEBUG:
        return

    print('DEBUG:', name, *a, file=sys.stderr)


def error(msg, code=1):
    print(msg, file=sys.stderr)

    if code > 0:
        sys.exit(code)


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
    p.add_argument('--command', '-c', type=str, required=True, help='Command to execute')
    # p.add_argument('--timeout', '-t', type=int, default=0, help='Timeout for single process')
    p.add_argument('--no-shell', default=False, action='store_true', help='Run command through shell')
    p.add_argument('--exit-code', type=int, default=1, help='Exit code on exceeded limit')
    p.add_argument('--dir-perms', type=str, default='700', help='Permissions to DB directory')
    p.add_argument('--file-perms', type=str, default='600', help='Permissions to DB files')
    p.add_argument('--debug', action='store_true', help='')

    args = p.parse_args(args)
    if args.debug:
        global DEBUG
        DEBUG = True

    args.dir_perms = int(args.dir_perms, 8)
    args.file_perms = int(args.file_perms, 8)

    return args


def main():
    args = parse_args(sys.argv[1:])

    if args.no_shell:
        command = shlex.split(args.command)
    else:
        command = args.command

    # if args.timeout <= 0:
    #     args.timeout = None

    lock_file_name = get_file_name(str(args.command).encode())

    tmp_dir = tempfile.gettempdir()
    debug('tmp_dir', tmp_dir)

    path = pathlib.Path(tmp_dir) / DB_NAME
    try:
        path.mkdir(args.dir_perms)
    except FileExistsError:
        try:
            os.chmod(str(path), args.dir_perms)
        except PermissionError as ex:
            error("Can't change permissions to %s: %s" % (path, ex))
    except OSError as ex:
        error("Can't create directory %s: %s" % (path, ex))

    lock_file_path = path / lock_file_name
    debug('lock_file_path', lock_file_path)

    try:
        with lock_file_path.open('a+'):
            try:
                os.chmod(str(lock_file_path), args.file_perms)
            except PermissionError as ex:
                error("Can't change permissions to %s: %s" % (lock_file_path, ex))

            cnt = count_descriptors(str(lock_file_path))
            if (cnt - 1) >= args.limit:  # minus current process
                print('Limit of processes is exceeded, exiting', file=sys.stderr)
                sys.exit(args.exit_code)

            proc = subprocess.Popen(command, shell=not args.no_shell)
            # proc.wait(timeout=args.timeout)
            proc.wait()
    except OSError as ex:
        error(str(ex))

    sys.exit(proc.returncode)


if __name__ == '__main__':
    main()
