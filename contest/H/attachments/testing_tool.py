#!/usr/bin/env python3

"""
Local testing tool for 'Secret Lilies and Roses'.

Disclaimer: This is *not* the same code used to test your solution when it is
submitted. The purpose of this tool is to help with debugging the interactive
problem and it has no ambitions to extensively test all possibilities that
are allowed by the problem statement. While the tool tries to yield the same
results as the real judging system, this is not guaranteed and the result
may differ if the tested program does not use the correct formatting or
exhibits other incorrect behavior. It also *does not* apply the time and
memory limits that are applied to submitted solutions.

The behavior is controlled by an input data file with t + 1 lines. The first
line contains the integer t. Each of the next t lines represents a single test
case. Each test case contains a string of n characters, where n is the number of
flowers for the test case. The i-th character is 'l' if flower i is a lily, or
'r' if flower i is a rose.

To run the testing tool, run::

    pypy3 testing_tool.py <input file> <program> <arguments>

where `arguments` are optional arguments to the program to run. The following
show examples for different languages::

    pypy3 testing_tool.py test.in ./myprogram
    pypy3 testing_tool.py test.in java -cp . MyProgram
    pypy3 testing_tool.py test.in pypy3 myprogram.py

One can also pass `--verbose` (before the input file name) to see a log of the
complete interaction.
"""

import argparse
import subprocess
import sys
from typing import List, TextIO


MIN_T = 1
MAX_T = 100
MIN_N = 1
MAX_N = 100
MAX_QUERY = 10

CHAR_LILY = "l"
CHAR_ROSE = "r"

QUERY_LILY = "lily"
QUERY_ROSE = "rose"
QUERY_ANSWER = "answer"
QUERY_TYPE = "type"
QUERY_MULTI = "multi"


class WrongAnswer(RuntimeError):
    """Raised whenever an incorrect answer is received."""

    pass


def vprint(*args, verbose: bool, file: TextIO, **kwargs) -> None:
    """Print to `file`, and also to stdout if `verbose is true."""
    if verbose:
        print("< ", end="")
        print(*args, **kwargs)
        sys.stdout.flush()
    print(*args, file=file, flush=True, **kwargs)


def vreadline(data: TextIO, *, verbose: bool) -> str:
    """Read a line from `data`, and also log it to stdout if `verbose` is true."""
    line = data.readline()
    if verbose and line:
        print(">", line.rstrip("\n"))
    return line


def get_lr(flowers: str):
    n = len(flowers)

    l = [0] * (n + 1)
    for i in range(1, n + 1):
        l[i] = l[i - 1] + (1 if flowers[i - 1] == CHAR_LILY else 0)

    r = [0] * (n + 1)
    for i in range(n - 1, -1, -1):
        r[i] = r[i + 1] + (1 if flowers[i] == CHAR_ROSE else 0)

    return l, r


def interact(process: subprocess.Popen, inputs: List[str], *, verbose: bool) -> int:
    vprint(len(inputs), file=process.stdin, verbose=verbose)

    query_counts = []
    for flowers in inputs:
        n = len(flowers)
        l, r = get_lr(flowers)

        vprint(n, file=process.stdin, verbose=verbose)
        query_count = 0

        try:
            while True:
                line = vreadline(process.stdout, verbose=verbose)
                if line == "":
                    raise WrongAnswer("End of file received from team program")
                line_split = line.split()

                if len(line_split) != 2:
                    raise WrongAnswer(f"Invalid line: {line}")

                kind = line_split[0]

                if kind == QUERY_TYPE or kind == QUERY_MULTI:
                    query_count += 1
                    if query_count > MAX_QUERY:
                        raise WrongAnswer(
                            f"Team program made more than {MAX_QUERY} queries"
                        )

                if kind == QUERY_TYPE:
                    query_str = line_split[1]
                    if not query_str:
                        raise WrongAnswer(f"{QUERY_TYPE} parameter is empty")
                    if not query_str.isdigit():
                        raise WrongAnswer(
                            f"{QUERY_TYPE} parameter {query_str} is non-integer"
                        )
                    i = int(query_str)
                    if i < 1 or i > n:
                        raise WrongAnswer(
                            f"{QUERY_TYPE} parameter {i} is outside the allowed range [1, {n}]"
                        )
                    vprint(
                        QUERY_LILY if flowers[i - 1] == CHAR_LILY else QUERY_ROSE,
                        file=process.stdin,
                        verbose=verbose,
                    )

                elif kind == QUERY_MULTI:
                    query_str = line_split[1]
                    if not query_str:
                        raise WrongAnswer(f"{QUERY_MULTI} parameter is empty")
                    if not query_str.isdigit():
                        raise WrongAnswer(
                            f"{QUERY_MULTI} parameter {query_str} is non-integer"
                        )
                    j = int(query_str)
                    if j < 0 or j > n:
                        raise WrongAnswer(
                            f"{QUERY_MULTI} parameter {j} is outside the allowed range [0, {n}]"
                        )
                    vprint(l[j] * r[j], file=process.stdin, verbose=verbose)

                elif kind == QUERY_ANSWER:
                    answer_str = line_split[1]
                    if not answer_str:
                        raise WrongAnswer("Team program did not make any answer")
                    if not answer_str.isdigit():
                        raise WrongAnswer(
                            f"Team program answer {answer_str} is non-integer"
                        )
                    answer = int(answer_str)
                    if answer < 0 or answer > n:
                        raise WrongAnswer(
                            f"Team program answer {answer} is outside the allowed range [0, {n}]"
                        )
                    if l[answer] != r[answer]:
                        raise WrongAnswer(f"Team program made a wrong answer")
                    break
                else:
                    raise WrongAnswer(f"Invalid output line: {line}")
        except BrokenPipeError:
            raise WrongAnswer(
                "Error when sending response to team program - possibly exited"
            )
        query_counts.append(query_count)

    line = vreadline(process.stdout, verbose=verbose)
    if line.strip() != "":
        raise WrongAnswer("Found extraneous output from team program")
    return query_counts


def main() -> int:
    parser = argparse.ArgumentParser(
        usage="%(prog)s [--verbose] data.in program [args...]"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show interactions"
    )
    parser.add_argument("data")
    parser.add_argument("program", nargs=argparse.REMAINDER)

    args = parser.parse_args()
    if not args.program:
        parser.error("Must specify program to run")

    inputs = None
    with open(args.data, "r") as data:
        t_str = data.readline().strip()
        if not t_str.isdigit():
            raise ValueError(f"Input is invalid: t is non-integer")
        t = int(t_str)
        inputs = [data.readline().strip() for _ in range(t)]

        if any([line.strip() for line in data.readlines()]):
            raise ValueError("Input is invalid: Input contains extraneous characters")

    if len(inputs) < MIN_T or len(inputs) > MAX_T:
        raise ValueError(
            f"Input is invalid: t must be between {MIN_T} and {MAX_T}, "
            f"inclusive, but it has t={len(inputs)}"
        )
    for flowers in inputs:
        n = len(flowers)

        if n < MIN_N or n > MAX_N:
            raise ValueError(
                f"Input is invalid: n must be between {MIN_N} and {MAX_N}, "
                f"inclusive, but it has n={n}"
            )

        for flower in flowers:
            if flower not in [CHAR_LILY, CHAR_ROSE]:
                raise ValueError(f"Input is invalid: Found invalid character {flower}")

        l, r = get_lr(flowers)
        if not any([l[i] == r[i] for i in range(n + 1)]):
            raise ValueError(
                f"Input is invalid: The arrangement {flowers} does not have a solution"
            )

    process = subprocess.Popen(
        args.program,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        encoding="utf-8",
        errors="surrogateescape",
    )

    try:
        try:
            query_counts = interact(process, inputs, verbose=args.verbose)
        except WrongAnswer as exc:
            print("Wrong answer ({})".format(exc))
            return 1
        process.wait()
    finally:
        if process.poll() is None:
            try:
                process.terminate()
            except ProcessLookupError:  # Should be impossible, but just to be safe
                pass
        process.wait()
    if process.returncode < 0:
        print(f"Run-time error (process exited with signal {-process.returncode})")
        return 1
    elif process.returncode > 0:
        print(f"Run-time error (process exited with status {process.returncode})")
        return 1
    else:
        print(f"Accepted (query_count for each test case in order = {query_counts})")
        return 0


if __name__ == "__main__":
    sys.exit(main())
