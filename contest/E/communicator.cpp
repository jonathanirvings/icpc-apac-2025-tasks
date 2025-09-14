#include <algorithm>
#include <cassert>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cmath>
#include <iostream>
#include <fstream>
#include <numeric>
#include <vector>
#include <map>
#include <set>
#include <queue>
#include <functional>
#include <iomanip>
using namespace std;

constexpr int kMinN = 3;
constexpr int kMaxN = 200;
constexpr int kMaxQuery = 500;

void ac() {
  cerr << "AC" << endl;
  exit(0); 
}

void wa() {
  cerr << "WA" << endl;
  exit(0);
}

void wrong_answer(const char *err, ...) {
  (void)err;  // error message is not used for now.
  wa();
}

void judge_error(const char *err, ...) {
  (void)err;  // error message is not used for now.
  assert(!"Judge Error");
}

struct Parser {
  Parser(int n_, string expr_) :
    n(n_),
    expr(expr_),
    query(),
    ptr(0),
    qi(0) {}

  int n;
  string expr;
  string query;
  int ptr, qi;

  void invalid_syntax() {
    judge_error("The expression does not follow the syntax");
  }

  char eval_impl() {
    if (expr[ptr] == '(') {
      ptr++;
      char c1 = eval_impl();
      if (expr[ptr++] != '-') invalid_syntax();
      char c2 = eval_impl();
      if (expr[ptr++] != ')') invalid_syntax();

      return (c1 == '1' && c2 == '0') ? '1' : '0';
    } else if (expr[ptr] == 'x') {
      ptr++;
      return query[qi++];
    } else {
      invalid_syntax();
      return 0;
    }
  }

  char eval(string query_) {
    query = query_;
    ptr = 0;
    qi = 0;
    char ret = eval_impl();

    if (ptr != static_cast<int>(expr.size())) {
      invalid_syntax();
    }
    if (qi != n) {
      judge_error("Query variables are not fully consumed. This should not happen.");
    }
    return ret;
  }
};

int main(int argc, char* argv[]) {
  ifstream tc_in(argv[1]);
  // out = ofstream(argv[2]);
  
  string expr;
  tc_in >> expr;
  if (static_cast<int>(expr.size()) % 4 != 1) {
    judge_error("Input is invalid: character length is %d", static_cast<int>(expr.size()));
  }
  int n = (static_cast<int>(expr.size()) + 3) / 4;
  if (n < kMinN || n > kMaxN) {
    judge_error("Input is invalid: n=%d", n);
  }

  set<char> allowed_chars{'(', '-', ')', 'x'};
  for (char c : expr) {
    if (!allowed_chars.count(c)) {
      judge_error("Input is invalid: invalid character found=%c", c);
    }
  }

  Parser parser(n, expr);
  string query0 = string(n, '0');
  (void)parser.eval(query0); // dry run to detect judge error

  cout << n << endl;

  int query_count = 0;
  while (1) {
    string kind;
    if (!(cin >> kind)) {
      wrong_answer("Contestant did not make any output");
    }

    if (kind == "query") {
      query_count++;
      if (query_count > kMaxQuery) {
        wrong_answer(
            "Contestant did make more than %d queries",
            kMaxQuery);
      }

      string query;
      if (!(cin >> query)) {
        wrong_answer("Contestant did not make any query");
      }
      if (static_cast<int>(query.size()) != n) {
        wrong_answer("Submission is invalid: length expected=%d but found=%d",
                     n, query.size());
      }
      for (char c : query) {
        if (c != '0' && c != '1') {
          wrong_answer("Submission is invalid: invalid character found=%c", c);
        }
      }

      char res = parser.eval(query);
      cout << res << endl;
    }
    else if (kind == "answer") {
      string guess;
      if (!(cin >> guess)) {
        wrong_answer("Contestant did not make any guess");
      }
      if (expr != guess) {
        wrong_answer("Contestant made a wrong guess");
      }

      string buffer;
      if (cin >> buffer) {
        wrong_answer("Found extraneous output: %s", buffer.c_str());
      }

      ac();
    }
    else {
      wrong_answer("Invalid output line: %s", kind.c_str());
    }
  }
}
