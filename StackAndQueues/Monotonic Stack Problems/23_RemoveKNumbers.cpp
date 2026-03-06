#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
    string removeKdigits(string num, int k) {
        int n = num.size();
        stack<char> st;

        for(auto ch : num){
            while(!st.empty() && st.top()>ch && k){
                st.pop();
                k--;
            }
            st.push(ch);
        }

        while(!st.empty() && k){
            st.pop();
            k--;
        }
        string ans = "";
        while(!st.empty()){
            ans += st.top();
            st.pop();
        }

        while(ans.size()>0 && ans.back()=='0'){
            ans.pop_back();
        }
        if(ans.size()==0){
            return "0";
        }
        reverse(ans.begin(),ans.end());
        return ans;
    }
};

int main() {
    return 0;
}