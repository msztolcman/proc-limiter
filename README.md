# proc-limiter
Do not allow to start more then LIMIT instances of your program.

It's very useful ie for programs running from CRON.

## Usage

```shell
usage: proc_limiter.py [-h] [--limit LIMIT] [--command COMMAND] [--no-shell]
                         [--exit-code EXIT_CODE]

optional arguments:
-h, --help            show this help message and exit
--limit LIMIT, -l LIMIT
                      Max number of processes
--command COMMAND, -c COMMAND
                      Command to execute
--no-shell            Run command through shell
--exit-code EXIT_CODE
                      Exit code on exceeded limit
```
