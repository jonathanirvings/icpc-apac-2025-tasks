#!/usr/bin/env python3

"""
Local testing tool for 'Sum of Three Cubes'.

Disclaimer: This is *not* the same code used to test your solution when it is
submitted. The purpose of this tool is to help with debugging the problem
that accepts multiple outputs. While the tool tries to yield the same results
as the real judging system, this is not guaranteed and the result may differ
if the output does not use the correct formatting.

You can create a file containing the output of your program using the content
of an input file as the input. For example, run::

    <program> < <input file> > <output file>

The following show examples for different languages::

    ./myprogram < test.in > test.out
    java -cp . MyProgram < test.in > test.out
    pypy3 myprogram.py < test.in > test.out

Afterwards, to run the testing tool, run::

    pypy3 testing_tool.py <input file> <output file>

For example::

    pypy3 testing_tool.py test.in test.out
"""

import argparse
from dataclasses import dataclass
import sys


MIN_N = 0
MAX_N = 50
MIN_XYZ = -10**18
MAX_XYZ = 10**18


class WrongAnswer(RuntimeError):
    """Raised whenever an incorrect answer is received."""

    pass


def check_integer(s: str):
    if s.isdigit():
        return True
    return len(s) > 1 and s[0] == '-' and s[1:].isdigit()


def check_output(n: int, output_lines: list[str]):
    if len(output_lines) < 1:
        raise WrongAnswer("The output must contain at least one line")

    line = output_lines[0]
    nums = line.split()
    if len(nums) != 3:
        raise WrongAnswer("The line must contains three integers")
    
    if any(not check_integer(num) for num in nums):
        raise WrongAnswer("The line must contains three integers")

    x = int(nums[0])
    y = int(nums[1])
    z = int(nums[2])

    if not (MIN_XYZ <= x <= MAX_XYZ):
        raise WrongAnswer(
            f"The value of x must be between "
            f"{MIN_XYZ} and {MAX_XYZ}, inclusive. x={x} is found"
        )
    if not (MIN_XYZ <= y <= MAX_XYZ):
        raise WrongAnswer(
            f"The value of y must be between "
            f"{MIN_XYZ} and {MAX_XYZ}, inclusive. y={y} is found"
        )
    if not (MIN_XYZ <= x <= MAX_XYZ):
        raise WrongAnswer(
            f"The value of z must be between "
            f"{MIN_XYZ} and {MAX_XYZ}, inclusive. z={z} is found"
        )

    if x**3 + y**3 + z**3 != n:
        raise WrongAnswer(
            f"The sum of cubes of x, y, and z does not match n={n}"
        )

    if any([line.strip() for line in output_lines[1:]]):
        raise WrongAnswer("The output contains extraneous characters")


def main() -> int:
    parser = argparse.ArgumentParser(usage="%(prog)s data.in data.out")
    parser.add_argument("data")
    parser.add_argument("output")
    args = parser.parse_args()

    with open(args.data, "r") as judgein:
        line = judgein.readline()
        if not line:
            raise ValueError("Invalid input: The first line must contain n")
        parts = line.split()
        if len(parts) < 1:
            raise ValueError("Invalid input: The first line must contain n")

        if not check_integer(parts[0]):
            raise ValueError("Invalid input: The first line must contain n")
        n = int(parts[0])
        if not (MIN_N <= n <= MAX_N):
            raise ValueError(
                f"Invalid input: n must be between {MIN_N} and {MAX_N}, "
                f"inclusive. n={n} is found"
            )
        if n % 9 == 4 or n % 9 == 5:
            raise ValueError(
                "Invalid input: n must not be equal to 4 or 5 modulo 9. "
                f"n={n} is found"
            )

    with open(args.output, "r") as conans:
        output_lines = conans.readlines()

    try:
        check_output(n, output_lines)
    except WrongAnswer as exc:
        print("Wrong answer ({})".format(exc))
        return 1

    print("Accepted")
    return 0


if __name__ == "__main__":
    sys.exit(main())
