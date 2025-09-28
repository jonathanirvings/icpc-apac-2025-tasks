#!/usr/bin/env python3

"""
Local testing tool for 'Three-Dimensional Embedding'.

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


MIN_N = 2
MAX_N = 1600
MIN_M = 1
MAX_M = 4000
MIN_COORD = 0
MAX_COORD = 400
MIN_K = 2
MAX_K = 30


class WrongAnswer(RuntimeError):
    """Raised whenever an incorrect answer is received."""

    pass


@dataclass
class Graph:
    n: int
    m: int
    edges: list[tuple[int, int]]


def sign(w: int):
    if w == 0:
        return 0
    return 1 if w > 0 else -1


@dataclass
class Array3D:
    size = 0
    val: bytearray

    def __init__(self, size):
        self.size = size
        self.val = bytearray(self.size**3)

    def get(self, x: int, y: int, z: int):
        return self.val[x * self.size**2 + y * self.size + z]

    def set(self, x: int, y: int, z: int, value: int):
        self.val[x * self.size**2 + y * self.size + z] = value


Point = tuple[int, int, int]


def check(used: Array3D, start: Point, end: Point, last_segment: bool, j: int):
    x0, y0, z0 = start
    x1, y1, z1 = end
    if abs(x0 - x1) + abs(y0 - y1) + abs(z0 - z1) == 0:
        raise WrongAnswer(
            f"All segments in polyline {j + 1} must have a positive length"
        )

    if (x0 != x1) + (y0 != y1) + (z0 != z1) != 1:
        raise WrongAnswer(
            f"All segments in polyline {j + 1} must be "
            "parallel to one of the x-, y-, or z-axis"
        )
    dx = sign(x1 - x0)
    dy = sign(y1 - y0)
    dz = sign(z1 - z0)
    assert not (
        dx == 0 and dy == 0 and dz == 0
    ), "Segment has no direction. This shouldn't happen."
    x = x0
    y = y0
    z = z0
    for _ in range(2 * MAX_COORD):
        x += dx
        y += dy
        z += dz
        done = x == x1 and y == y1 and z == z1
        if last_segment and done:
            assert used.get(
                x, y, z
            ), "Endpoint is marked as non-used. This shouldn't happen."
            return
        if used.get(x, y, z) != 0:
            raise WrongAnswer(
                f"Polylines contain intersections at a point ({x}, {y}, {z}), "
                "which may be a self-intersection, an intersection of two "
                "distinct polylines, or a some embedded point."
            )
        used.set(x, y, z, 1)
        if done:
            return
    assert False, "So many iterations. This shouldn't happen."


def check_output(graph: Graph, output_lines: list[str]):
    used = Array3D(MAX_COORD + 2)

    if len(output_lines) < graph.n + graph.m:
        raise WrongAnswer(
            f"The output must contain n+m lines. Only {len(output_lines)} lines are given"
        )

    embp = []
    for i in range(graph.n):
        line = output_lines[i]
        if not line:
            raise WrongAnswer(f"A line for vertex {i + 1} is not given")
        nums = line.split()
        if len(nums) != 2:
            raise WrongAnswer(
                f"A line for vertex {i + 1} must contain exactly two integers"
            )

        if any(not num.isdigit() for num in nums):
            raise WrongAnswer(
                f"A line for vertex {i + 1} must contain exactly two integers"
            )
        x = int(nums[0])
        y = int(nums[1])

        if not (MIN_COORD <= x <= MAX_COORD):
            raise WrongAnswer(
                f"x-coordinate of point {i + 1} must be between "
                f"{MIN_COORD} and {MAX_COORD}, inclusive. x={x} is found"
            )
        if not (MIN_COORD <= y <= MAX_COORD):
            raise WrongAnswer(
                f"y-coordinate of point {i + 1} must be between "
                f"{MIN_COORD} and {MAX_COORD}, inclusive. y={y} is found"
            )
        z = 0
        if used.get(x, y, z) != 0:
            raise WrongAnswer(
                f"Two or more vertices are embedded as the same point ({x}, {y}, {z})"
            )
        used.set(x, y, z, 1)
        embp.append((x, y, z))

    for j in range(graph.m):
        line = output_lines[graph.n + j]
        if not line:
            raise WrongAnswer(f"A line for polyline {j + 1} is not given")
        nums = line.split()
        if len(nums) < 1:
            raise WrongAnswer(f"A line for polyline {j + 1} is not given")

        if any(not num.isdigit() for num in nums):
            raise WrongAnswer(f"A line for polyline {j + 1} must contain only integers")

        k = int(nums[0])
        if not (MIN_K <= k <= MAX_K):
            raise WrongAnswer(
                f"The number of nodes k in a line for polyline {j + 1} must be "
                f"an integer between {MIN_K} and {MAX_K}, inclusive"
            )
        if len(nums) != 3 * k + 1:
            raise WrongAnswer(
                f"A line for polyline {j + 1} must contain 3k+1 integers. "
                f"k={k} is specified, while the line contains {len(nums)} elements"
            )

        poly = []
        for r in range(k):
            x = int(nums[1 + 3 * r])
            y = int(nums[2 + 3 * r])
            z = int(nums[3 + 3 * r])

            if not (MIN_COORD <= x <= MAX_COORD):
                raise WrongAnswer(
                    f"x-coordinate for a node of polyline {j + 1} must be between "
                    f"{MIN_COORD} and {MAX_COORD}, inclusive. x={x} is given"
                )
            if not (MIN_COORD <= y <= MAX_COORD):
                raise WrongAnswer(
                    f"y-coordinate for a node of polyline {j + 1} must be between "
                    f"{MIN_COORD} and {MAX_COORD}, inclusive. y={y} is given"
                )
            if not (MIN_COORD <= z <= MAX_COORD):
                raise WrongAnswer(
                    f"z-coordinate for a node of polyline {j + 1} must be between "
                    f"{MIN_COORD} and {MAX_COORD}, inclusive. z={z} is given"
                )
            poly.append((x, y, z))

        v, w = graph.edges[j]
        v -= 1
        w -= 1
        if poly[0] != embp[v]:
            raise WrongAnswer(
                f"The first endpoint of polyline {j + 1} must "
                f"match to vertex {v + 1}"
            )
        if poly[-1] != embp[w]:
            raise WrongAnswer(
                f"The last endpoint of polyline {j + 1} must "
                f"match to vertex {w + 1}"
            )
        for r in range(1, k):
            check(used, poly[r - 1], poly[r], r == (k - 1), j)

    if any([line.strip() for line in output_lines[graph.n + graph.m :]]):
        raise WrongAnswer("The output contains extraneous characters")


def main() -> int:
    parser = argparse.ArgumentParser(usage="%(prog)s data.in data.out")
    parser.add_argument("data")
    parser.add_argument("output")
    args = parser.parse_args()

    with open(args.data, "r") as judgein:
        line = judgein.readline()
        if not line:
            raise ValueError("Invalid input: The first line must contain n and m")
        parts = line.split()
        if len(parts) < 2:
            raise ValueError("Invalid input: The first line must contain n and m")

        if any(not part.isdigit() for part in parts):
            raise ValueError("Invalid input: The first line must contain n and m")
        n = int(parts[0])
        m = int(parts[1])
        if not (MIN_N <= n <= MAX_N):
            raise ValueError(
                f"Invalid input: n must be between {MIN_N} and {MAX_N}, "
                f"inclusive. n={n} is found"
            )
        if not (MIN_M <= m <= MAX_M):
            raise ValueError(
                f"Invalid input: m must be between {MAX_M} and {MAX_M}, "
                f"inclusive. m={m} is found"
            )

        degs = [0] * n
        edges = set()
        edge_list = []
        for j in range(m):
            line = judgein.readline()

            if not line:
                raise ValueError(f"Invalid input: Edge {j + 1} is not read")

            parts = line.split()
            if len(parts) < 2:
                raise ValueError(
                    f"Invalid input: A line for edge {j + 1} must "
                    "contain exactly two integers"
                )

            if any(not part.isdigit() for part in parts):
                raise ValueError(
                    f"Invalid input: A line for edge {j + 1} must "
                    "contain exactly two integers"
                )
            v = int(parts[0])
            w = int(parts[1])
            if not (1 <= v < w <= n):
                raise ValueError(
                    f"Invalid input: A line for edge {j + 1} is not "
                    "satisfying the constraint"
                )
            if (v, w) in edges:
                raise ValueError("Invalid input: There must not be parallel edges")
            edges.add((v, w))
            edge_list.append((v, w))
            v -= 1
            w -= 1
            degs[v] += 1
            degs[w] += 1

        for i in range(n):
            if degs[i] > 5:
                raise ValueError(
                    f"Invalid input: Vertex {i + 1} must be "
                    "incident to at most five edges."
                )

    graph = Graph(n=n, m=m, edges=edge_list)

    with open(args.output, "r") as conans:
        output_lines = conans.readlines()

    try:
        check_output(graph, output_lines)
    except WrongAnswer as exc:
        print("Wrong answer ({})".format(exc))
        return 1

    print("Accepted")
    return 0


if __name__ == "__main__":
    sys.exit(main())
