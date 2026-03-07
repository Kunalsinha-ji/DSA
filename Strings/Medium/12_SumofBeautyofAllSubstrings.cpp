#include <bits/stdc++.h>
using namespace std;

// 0(n*n *26) is best

class Solution {
public:
    int beautySum(string s) {
        int n = s.size();
        int ans = 0;

        for(int i = 0; i < n; i++){
            int freq[26] = {0};
            int maxFreq = 0;

            for(int j = i; j < n; j++){
                int idx = s[j] - 'a';
                freq[idx]++;

                maxFreq = max(maxFreq, freq[idx]);

                int minFreq = INT_MAX;
                for(int k = 0; k < 26; k++){
                    if(freq[k] > 0){
                        minFreq = min(minFreq, freq[k]);
                    }
                }

                ans += (maxFreq - minFreq);
            }
        }

        return ans;
    }
};

int main() {
    return 0;
}