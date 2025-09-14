#include <fstream>
#include <iostream>
#include <string>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cassert>
#include <cmath>
#include <cstdarg>
#include <vector>
#include <tuple>
#include <set>

std::ifstream judgein, judgeans, conans;
FILE *judgemessage = NULL;
FILE *diffpos = NULL;
int judgeans_pos, con_pos;
int judgeans_line, con_line;

void ac() {
  puts("AC");
  exit(0); 
}

void wa() {
  puts("WA");
  exit(0);
}

void wrong_answer(const char *err, ...) {
#ifdef DEBUG_EMBEDDING
  va_list pvar;
  va_start(pvar, err);
  vfprintf(stderr, err, pvar);
#endif
  wa();
}

void judge_error(const char *err, ...) {
  va_list pvar;
  va_start(pvar, err);
  // If judgemessage hasn't been set up yet, write error to stderr
  if (!judgemessage) judgemessage = stderr;
  vfprintf(judgemessage, err, pvar);
  fprintf(judgemessage, "\n");
  assert(!"Judge Error");
}

template <typename Stream>
void openfile(Stream &stream, const char *file, const char *whoami) {
  stream.open(file);
  if (stream.fail()) {
    judge_error("%s: failed to open %s\n", whoami, file);
  }
}

FILE *openfeedback(const char *feedbackdir, const char *feedback, const char *whoami) {
  std::string path = std::string(feedbackdir) + "/" + std::string(feedback);
  FILE *res = fopen(path.c_str(), "w");
  if (!res) {
    judge_error("%s: failed to open %s for writing", whoami, path.c_str());
  }
  return res;
}

/////////////////////////////////////////////////////////////////////////////////////

bool v[402][402][402];

using P = std::tuple<int, int, int>;

int sign(int w) {
  if (w == 0) return 0;
  return w > 0 ? 1 : -1;
}

void check(P start, P end, bool last_segment) {
  int x0, y0, z0, x1, y1, z1;
  std::tie(x0, y0, z0) = start;
  std::tie(x1, y1, z1) = end;
  if ((x0 != x1) + (y0 != y1) + (z0 != z1) != 1) wrong_answer("The segment must be parallel to one of x-, y-, or z-axis and have non-zero length");

  int dx = sign(x1 - x0),
      dy = sign(y1 - y0),
      dz = sign(z1 - z0);

  if (dx == 0 && dy == 0 && dz == 0) judge_error("Segment has no direction. This shouldn't happen!");

  for (int x = x0 + dx, y = y0 + dy, z = z0 + dz, it = 0;
      it <= 800;
      x += dx, y += dy, z += dz, it++) {
    bool done = (x == x1) && (y == y1) && (z == z1);
    if (last_segment && done) {
      if (!v[x][y][z]) judge_error("Endpoint is marked as non-visited. This shouldn't happen!");
      return;
    }

    if (v[x][y][z]) wrong_answer("Polylines contain intersections (self-intersections, intersection of two distinct polylines, or containing some embedded points).");
    v[x][y][z] = 1;

    if (done) return;
  }

  judge_error("So many iterations. This shouldn't happen!");
}

const char *USAGE = "Usage: %s judge_in judge_ans contestant_ans";

int main(int argc, char **argv) {
  if(argc < 4) {
    judge_error(USAGE, argv[0]);
  }
  openfile(judgein, argv[1], argv[0]);
  openfile(judgeans, argv[2], argv[0]); // non-used here
  openfile(conans, argv[3], argv[0]);

  int n, m;
  if (!(judgein >> n >> m)) judge_error("input broken! n and m not found");
  if (n < 2 || n > 1600) judge_error("n is invalid: n=%d found", n);
  if (m < 1 || m > 4000) judge_error("m is invalid: m=%d found", m);

  std::vector<int> degs(n);
  std::vector<int> u(m), w(m);
  std::set<std::pair<int, int>> edges;
  for (int j = 0; j < m; ++j) {
    if (!(judgein >> u[j] >> w[j])) judge_error("Edge %d was not read", j + 1);
    if (!(1 <= u[j] && u[j] < w[j] && w[j] <= n)) judge_error("Edge %d is not satisfying the constraint");
    if (edges.count({u[j], w[j]})) judge_error("Multi edge was found");
    edges.insert({u[j], w[j]});

    u[j]--;
    w[j]--;

    degs[u[j]]++;
    degs[w[j]]++;
  }
  for (int i = 0; i < n; ++i) if (degs[i] > 5) judge_error("Vertex %i has more than five degrees", i + 1);

  memset(v, 0, sizeof(v));
  std::vector<P> embp(n);
  for (int i = 0; i < n; ++i) {
    int x, y;
    if (!(conans >> x >> y)) wrong_answer("Point %d was not given", i + 1);
    if (!(0 <= x && x <= 400)) wrong_answer("x-coordinate of point %d is invalid: x=%d", i + 1, x);
    if (!(0 <= y && y <= 400)) wrong_answer("y-coordinate of point %d is invalid: x=%d", i + 1, y);
    int z = 0;

    embp[i] = P(x, y, z);
    if (v[x][y][z]) wrong_answer("Point at (%d, %d, %d) is used twice", x, y, z);
    v[x][y][z] = 1;
  }

  std::vector<std::vector<P>> poly_list(m);
  for (int j = 0; j < m; ++j) {
    int k;
    if (!(conans >> k)) wrong_answer("k was not given for edge %d", j + 1);
    if (k < 2 || k > 30) wrong_answer("k is invalid for edge %d: k=%d", j + 1, k);
    std::vector<P> poly(k);
    for (int p = 0; p < k; ++p) {
      int x, y, z;
      if (!(conans >> x >> y >> z)) wrong_answer("Nodes of polyline %d were not fully given", j + 1);
      if (!(0 <= x && x <= 400)) wrong_answer("A node of polyline %d is out of range: x=%d", j + 1, x);
      if (!(0 <= y && y <= 400)) wrong_answer("A node of polyline %d is out of range: y=%d", j + 1, y);
      if (!(0 <= z && z <= 400)) wrong_answer("A node of polyline %d is out of range: z=%d", j + 1, z);
      poly[p] = P(x, y, z);
    }

    if (poly[0] != embp[u[j]]) wrong_answer("Endpoint of polyline %d is mismatching", j + 1);
    if (poly[k - 1] != embp[w[j]]) wrong_answer("Endpoint of polyline %d is mismatching", j + 1);

    for (int p = 1; p < k; ++p) {
      check(poly[p - 1], poly[p], p == (k - 1));
    }

    poly_list[j] = poly;
  }

  // double checking
  int n_visited = 0;
  for (int x = 0; x <= 400; ++x) {
    for (int y = 0; y <= 400; ++y) {
      for (int z = 0; z <= 400; ++z) {
        n_visited += v[x][y][z];
      }
    }
  }
  int total_len = n;
  for (int j = 0; j < m; ++j) {
    std::vector<P> poly = poly_list[j];
    int k = static_cast<int>(poly.size());
    for (int p = 1; p < k; ++p) {
      int x0, y0, z0, x1, y1, z1;
      std::tie(x0, y0, z0) = poly[p - 1];
      std::tie(x1, y1, z1) = poly[p];
      total_len += abs(x0 - x1) + abs(y0 - y1) + abs(z0 - z1);
    }
    total_len--; // last one
  }
  if (total_len != n_visited) judge_error("Double check failed: total_len=%d; n_visited=%d", total_len, n_visited);

  std::string team;
  if (conans >> team) {
    wrong_answer("Trailing output:\n%s", team.c_str());
  }

  ac();
}
