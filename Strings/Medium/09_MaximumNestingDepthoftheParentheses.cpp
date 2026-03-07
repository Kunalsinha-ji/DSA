#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
    int maxDepth(string s) {
        int ans = 0;
        int c = 0;
        for(auto it: s){
            if(it=='('){
                c++;
                ans = max(ans,c);
            }
            else if(it==')'){
                c--;
            }
            else{
                continue;
            }
        }
        return ans;
    }
};

int main() {
    return 0;
}