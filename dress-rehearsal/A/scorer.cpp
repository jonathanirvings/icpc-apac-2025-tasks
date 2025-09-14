#include <bits/stdc++.h>
using namespace std;

int ac() {
  puts("AC");
  return 0;
}

int wa(string message) {
  fprintf(stderr, "%s\n", message.c_str());
  puts("WA");
  return 0;
}

void judge_error(const char *err, ...) {
  va_list pvar;
  va_start(pvar, err);
  // If judgemessage hasn't been set up yet, write error to stderr
  assert(!"Judge Error");
}

typedef string BigInteger;

const int MIN_N = 0;
const int MAX_N = 50;
const long long MIN_VALUE = -1000000000000000000LL;
const long long MAX_VALUE = 1000000000000000000LL;

BigInteger toBigInteger(long long x) {
  string res = "";
  while (x > 0) {
    res += (char)(x % 10 + '0');
    x /= 10;
  }
  return res;
}

BigInteger add(BigInteger x, BigInteger y) {
  while (x.size() < y.size()) {
    x += '0';
  }
  while (y.size() < x.size()) {
    y += '0';
  }
  string res = "";
  int carry = 0;
  for (int i = 0; i < x.size(); ++i) {
    res += (char)((x[i] - '0' + y[i] - '0' + carry) % 10 + '0');
    carry = (x[i] - '0' + y[i] - '0' + carry) / 10;
  }
  if (carry) {
    res += (char)(carry + '0');
  }
  return res;
}

BigInteger mul(BigInteger x, long long y) {
  if (y == 1) {
    return x;
  }
  BigInteger xy_div_two = mul(x, y / 2);
  BigInteger xy = add(xy_div_two, xy_div_two);
  if (y % 2 == 0) {
    return xy;
  }
  return add(xy, x);
}

BigInteger pow3(long long x) {
  return mul(mul(toBigInteger(x), x), x);
}

// [jgs] Commented lines are modification from the original
int main(int argc, char *argv[])
{
  FILE *in = fopen(argv[1], "r");
  // FILE *out = fopen(argv[2], "r");  // Judge's
  FILE *con = fopen(argv[3], "r");

  int N;
  fscanf(in, "%d\n", &N);

  if (N < MIN_N || N > MAX_N || N % 9 == 4 || N % 9 == 5) {
    judge_error("Value of N is invalid");
  }

  BigInteger lhs = toBigInteger(N);
  BigInteger rhs = toBigInteger(0);

  // long long judge;
  // fscanf(out, "%lld", &judge);
  
  // if (fscanf(out, "%lld", &judge) == EOF) {
  //   long long contestant;
  //   if (fscanf(con, "%lld", &contestant) != 1) {
  //     return wa("Unexpected EOF.");
  //   }
  //   if (contestant != IMPOSSIBLE_KEY) {
  //     return wa("Judge answer is `impossible`, contestant answer is not.");
  //   }
  // } else {
  {
    for (int i = 0; i < 3; ++i) {
      long long contestant;
      if (fscanf(con, "%lld", &contestant) != 1) {
        return wa("Unexpected EOF.");
      }
      if (contestant < MIN_VALUE || contestant > MAX_VALUE) {
        return wa("Contestant output out of bound.");
      }
      if (contestant < 0) {
        lhs = add(lhs, pow3(abs(contestant)));
      } else if (contestant > 0) {
        rhs = add(rhs, pow3(contestant));
      }
    }

    if (lhs != rhs) {
      return wa("X^3 + Y^3 + Z^3 != N");
    }
  }

  fscanf(con, "\n");
  char dummy;
  if (fscanf(con, "%c", &dummy) == 1) {
    return wa("Expected EOF.");
  }

  return ac();
}