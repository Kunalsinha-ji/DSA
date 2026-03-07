#include <bits/stdc++.h>
using namespace std;

// O(N)
class Solution {
public:
    string removeOuterParentheses(string s) {
        string ans = "";
        int c = 0;

        for(int i=0;i<s.size();i++){
            if(s[i]=='('){
                c++;
                if(c==1){
                    continue;
                }
                ans += "(";
            }
            else{
                c--;
                if(c==0){
                    continue;
                }
                ans += ")";
            }
        }
        return ans;
    }
};

int main() {
    return 0;
}