#include <bits/stdc++.h>
using namespace std;

constexpr int MAX_T = 100;
constexpr int MAX_N = 100;
constexpr int MAX_QUERY = 10;

constexpr char CHAR_LILY = 'l';
constexpr char CHAR_ROSE = 'r';

const string LILY = "lily";
const string ROSE = "rose";
const string ANSWER = "answer";
const string TYPE_QUERY = "type";
const string MULTIPLY_QUERY = "multi";

void ac() {
	cerr << "AC" << endl;
	exit(0); 
}

void wa() {
	cerr << "WA" << endl;
	exit(0);
}

void wrongAnswer(const char *err, ...) {
	(void) err;	// error message is not used for now
	wa();
}

void judgeError(const char *err, ...) {
	(void) err;	// error message is not used for now
	assert(!"Judge Error");
}

int main(int argc, char* argv[]) {
	ifstream tc_in(argv[1]);
	// out = ofstream(argv[2]);
	
	int T;
	tc_in >> T;
	if (T < 1 || T > MAX_T) {
		judgeError("Invalid input: T = %d is not between 1 to %d", T, MAX_T);
	}
	
	vector<string> SECRET;
	for (int tc = 0; tc < T; tc++) {
		string S;
		tc_in >> S;
		
		int N = S.length();
		if (N < 1 || N > MAX_N) {
			judgeError("Invalid input: [TC %d] N = %d is not between 1 to %d", tc, N, MAX_N);
		}
		
		for (int i = 0; i < N; i++) {
			if (S[i] != CHAR_LILY && S[i] != CHAR_ROSE) {
				judgeError("Invalid input: [TC %d] The %d-th character = %c is neither %c nor %c", tc, i + 1, S[i], CHAR_LILY, CHAR_ROSE);
			}
		}
		
		vector<int> l(N + 1, 0), r(N + 1, 0);
		
		for (int i = 1; i <= N; i++) {
			l[i] = l[i-1] + (S[i-1] == CHAR_LILY ? 1 : 0);
		}
		
		for (int i = N-1; i >= 0; i--) {
			r[i] = r[i+1] + (S[i] == CHAR_ROSE ? 1 : 0);
		}
		
		bool hasAnswer = false;
		for (int i = 0; i <= N; i++) {
			hasAnswer |= (l[i] == r[i]);
		}
		
		if (!hasAnswer) {
			judgeError("Invalid input: [TC %d] The arrangement doesn't have an ANSWER", tc);
		}
		
		SECRET.push_back(S);
	}
	
	cout << T << endl;
	for (int tc = 0; tc < T; tc++) {
		string S = SECRET[tc];
		int N = S.length();
		vector<int> l(N + 1, 0), r(N + 1, 0);
		
		for (int i = 1; i <= N; i++) {
			l[i] = l[i-1] + (S[i-1] == CHAR_LILY ? 1 : 0);
		}
		
		for (int i = N-1; i >= 0; i--) {
			r[i] = r[i+1] + (S[i] == CHAR_ROSE ? 1 : 0);
		}
		
		cout << N << endl;
		int numQuery = 0;
		
		while (true) {
			string query;
			if (!(cin >> query)) {
				wrongAnswer("[TC %d] Contestant doesn't make any query", tc);
			}
			
			if (query != ANSWER && query != TYPE_QUERY && query != MULTIPLY_QUERY) {
				wrongAnswer("[TC %d] Contestant writes an invalid query string", tc);
			}
			
			int idx;
			if (!(cin >> idx)) {
				wrongAnswer("[TC %d] Contestant writes an incomplete query", tc);
			}
			
			if (query == ANSWER) {
				if (idx < 0 || idx > N) {
					wrongAnswer("[TC %d] Contestant writes an invalid index for the answer", tc);
				} else if (l[idx] != r[idx]){
					wrongAnswer("[TC %d] Contestant gives an incorrect answer", tc);
				} else {
					break; // Contestant gives a correct answer
				}
				
			} else if (query == TYPE_QUERY) {
				numQuery++;
				if (numQuery > MAX_QUERY) {
					wrongAnswer("[TC %d] Contestant asks too much query", tc);
				} if (idx < 1 || idx > N) {
					wrongAnswer("[TC %d] Contestant writes an invalid index for the type query", tc);
				} else {
					cout << ((S[idx - 1] == CHAR_LILY) ? LILY : ROSE) << endl;
				}
				
			} else { // MULTIPLY_QUERY
				numQuery++;
				if (numQuery > MAX_QUERY) {
					wrongAnswer("[TC %d] Contestant asks too much query", tc);
				} if (idx < 0 || idx > N) {
					wrongAnswer("[TC %d] Contestant writes an invalid index for the multiply query", tc);
				} else {
					cout << l[idx] * r[idx] << endl;
				}
			}
		}
	}
	
	string buffer;
	if (cin >> buffer) {
		wrongAnswer("Contestant writes extraneous outputs");
	}
	ac();
}
