#include <bits/stdc++.h>
using namespace std;

// Trick >= then >

class Solution {
    bool isOperand(char ch){
        if(ch>='a' && ch<='z'){
            return true;
        }
        if(ch>='A' && ch<='Z'){
            return true;
        }
        if(ch>='0' && ch<='9'){
            return true;
        }
        return false;
    }
  public:
    string infixToPrefix(string &s) {
        int n = s.size();
        stack<char> st;
        string ans = "";
        unordered_map<char,int> priority;
        priority['/'] = 2;
        priority['*'] = 2;
        priority['+'] = 1;
        priority['-'] = 1;
        priority['^'] = 3;

        reverse(s.begin(),s.end());

        for(int i=0;i<n;i++){
            if(s[i]=='('){
                s[i] = ')';
            }
            else if(s[i]==')'){
                s[i] = '(';
            }
        }

        for(auto it: s){
            if(isOperand(it)){
                ans += it;
            }
            else if(it=='('){
                st.push(it);
            }
            else if(it==')'){
                while(!st.empty() && st.top()!='('){
                    ans += st.top();
                    st.pop();
                }
                if(!st.empty()){
                    st.pop();
                }
            }
            else{
                if(it=='^'){
                    while(!st.empty() && priority[st.top()]>=priority[it]){
                        ans += st.top();
                        st.pop();
                    }
                    st.push(it);
                }
                else{
                    while(!st.empty() && priority[st.top()]>priority[it]){
                        ans += st.top();
                        st.pop();
                    }
                    st.push(it);
                }
            }
        }
        while(!st.empty()){
            ans += st.top();
            st.pop();
        }
        reverse(ans.begin(),ans.end());
        return ans;
    }
};


int main() {
    return 0;
}