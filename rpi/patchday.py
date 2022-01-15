#!/usr/bin/env python3
from pathlib import Path
import os, subprocess, sys


RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"
BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(30, 38)


def Warn(x):
    return (COLOR_SEQ % (RED)) + x + RESET_SEQ

def Info(x, col=GREEN):
    return (COLOR_SEQ % (col)) + x + RESET_SEQ


def output_callback_svn_info(completed_process):
    # Zur Info: Welche Revision ist bisher verwendet worden?
    for line in completed_process.stdout.splitlines():
        if line.lower().startswith("last changed rev:") or \
           line.lower().startswith("letzte geänderte rev:"):
            print(Info(line))
        elif line:
            print(line)


def output_callback_check_yes(completed_process):
    out = completed_process.stdout.strip()
    yes = "yes"
    if out != yes:
        cmd = " ".join(completed_process.args)
        print(Warn(f'Die Ausgabe von `{cmd}` war nicht "{yes}", sondern "{out}"!'))


def run(cmd, cwd=None, output_callback=None, quiet=False):
    if not quiet:
        print(Info("\n{}$".format(cwd or ""), BLUE), Info(" ".join(cmd), BLUE))

    try:
        completed = subprocess.run(cmd, cwd=cwd, check=True, capture_output=(output_callback is not None), text=True)
    except OSError as e:
        print(Warn(e.strerror))
    except KeyboardInterrupt:
        print("(got Ctrl+C)")

    if output_callback:
        output_callback(completed)


def in_virtualenv():
    # Siehe http://stackoverflow.com/questions/1871549/python-determine-if-running-inside-virtualenv
    return hasattr(sys, 'real_prefix') or sys.base_prefix != sys.prefix


if __name__ == "__main__":
    # Laufen wir innerhalb einer virtualenv? (Sollte `pip` nicht ausführen, wenn das nicht der Fall ist.)
    if not in_virtualenv():
        print(Warn("\nEs scheint keine virtualenv aktiv zu sein.\n"))
        sys.exit()

    # run(["svn", "info", "."], output_callback=output_callback_svn_info)
    # run(["svn", "update"])
    run(["pip", "install", "-q", "-r", "requirements-ubuntu.txt"])

    # run(["python", "bookmaker.py", "--pdf"])

    # Stelle sicher, dass das System die richtige Uhrzeit verwendet.
    run(["timedatectl", "show", "--property", "CanNTP",          "--value"], output_callback=output_callback_check_yes, quiet=True)
    run(["timedatectl", "show", "--property", "NTP",             "--value"], output_callback=output_callback_check_yes, quiet=True)
    run(["timedatectl", "show", "--property", "NTPSynchronized", "--value"], output_callback=output_callback_check_yes, quiet=True)

    print("All done.\n")
