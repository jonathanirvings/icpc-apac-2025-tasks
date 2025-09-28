#!/usr/bin/env python3

"""
Local testing tool for 'Minus Operator'.

Disclaimer: This is *not* the same code used to test your solution when it is
submitted. The purpose of this tool is to help with debugging the interactive
problem and it has no ambitions to extensively test all possibilities that
are allowed by the problem statement. While the tool tries to yield the same
results as the real judging system, this is not guaranteed and the result
may differ if the tested program does not use the correct formatting or
exhibits other incorrect behavior. It also *does not* apply the time and
memory limits that are applied to submitted solutions.

The behavior is controlled by an input data file with a single line containing
an expression string that adheres to E.

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
from typing import TextIO


MIN_N = 3
MAX_N = 200
MAX_QUERY = 500


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


class Parser:
    def __init__(self, n, expr):
        self.n = n
        self.expr = expr

    def _invalid_syntax(self):
        raise ValueError("Invalid input: The expression does not follow the syntax")

    def _eval_impl(self, query, expr_idx, query_idx):
        if self.expr[expr_idx] == "(":
            expr_idx += 1

            c1, expr_idx, query_idx = self._eval_impl(query, expr_idx, query_idx)
            if expr_idx >= len(self.expr) or self.expr[expr_idx] != "-":
                self._invalid_syntax()
            expr_idx += 1

            c2, expr_idx, query_idx = self._eval_impl(query, expr_idx, query_idx)
            if expr_idx >= len(self.expr) or self.expr[expr_idx] != ")":
                self._invalid_syntax()
            expr_idx += 1

            return "1" if (c1 == "1" and c2 == "0") else "0", expr_idx, query_idx

        elif self.expr[expr_idx] == "x":
            expr_idx += 1
            if query_idx >= len(query):
                self._invalid_syntax()
            result = query[query_idx]
            query_idx += 1
            return result, expr_idx, query_idx

        else:
            self.invalid_syntax()

    def eval(self, query):
        result, expr_idx, _ = self._eval_impl(query, 0, 0)

        if expr_idx != len(self.expr):
            self._invalid_syntax()

        return result


def validate_expr(expr):
    n = (len(expr) + 3) // 4
    if len(expr) % 4 != 1:
        raise ValueError("Invalid input: The expression does not follow the syntax")
    allowed_chars = {"(", "-", ")", "x"}

    for c in expr:
        if c not in allowed_chars:
            raise ValueError(f"Invalid input: invalid character found='{c}'")

    parser = Parser(n, expr)
    parser.eval("0" * n)  # Check for invalid expression

    if n < MIN_N or n > MAX_N:
        raise ValueError(
            f"Input is invalid: n must be between {MIN_N} and {MAX_N}, "
            f"inclusive, but it has n={n}"
        )


def interact(process: subprocess.Popen, answer: str, *, verbose: bool) -> int:
    expr = answer
    n = (len(expr) + 3) // 4
    parser = Parser(n, expr)
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

            if kind == "query":
                query_count += 1
                if query_count > MAX_QUERY:
                    raise WrongAnswer(
                        f"Team program made more than {MAX_QUERY} queries"
                    )

                query_str = line_split[1]
                if not query_str:
                    raise WrongAnswer("Team program did not make any query")

                if len(query_str) != n:
                    raise WrongAnswer(
                        f"Query is invalid: length should be {n}, "
                        f"but actually it is {len(query_str)}"
                    )

                for c in query_str:
                    if c not in {"0", "1"}:
                        raise WrongAnswer(
                            f"Query is invalid: invalid character found='{c}'"
                        )

                res = parser.eval(query_str)

                vprint(res, file=process.stdin, verbose=verbose)

            elif kind == "answer":
                guess = line_split[1]
                if not guess:
                    raise WrongAnswer("Team program did not make any guess")
                if expr != guess:
                    raise WrongAnswer("Team program made a wrong guess")
                break
            else:
                raise WrongAnswer(f"Invalid output line: {line}")

    except BrokenPipeError:
        raise WrongAnswer(
            "Error when sending response to team program - possibly exited"
        )
    line = vreadline(process.stdout, verbose=verbose)
    if line.strip() != "":
        raise WrongAnswer("Found extraneous output from team program")
    return query_count


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

    answer = None
    with open(args.data, "r") as data:
        answer = data.readline().strip()
        validate_expr(answer)

        if any([line.strip() for line in data.readlines()]):
            raise ValueError("Input is invalid: Input contains extraneous characters")

    process = subprocess.Popen(
        args.program,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        encoding="utf-8",
        errors="surrogateescape",
    )
    try:
        try:
            query_count = interact(process, answer, verbose=args.verbose)
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
        print(f"Accepted (query_count = {query_count})")
        return 0


if __name__ == "__main__":
    sys.exit(main())
