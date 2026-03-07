#include <bits/stdc++.h>
using namespace std;

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
        reverse(s.begin(),s.end());
        unordered_map<char,int> priority;
        priority['^'] = 3;
        priority['*'] = 2;
        priority['/'] = 2;
        priority['-'] = 1;
        priority['+'] = 1;

        for(int i=0;i<n;i++){
            if(s[i]=='('){
                s[i]=')';
            }
            else if(s[i]==')'){
                s[i]='(';
            }
        }
        stack<char> st;
        string ans = "";

        for(int i=0;i<n;i++){
            if(isOperand(s[i])){
                ans += s[i];
            }
            else if(s[i]=='('){
                st.push(s[i]);
            }
            else if(s[i]==')'){
                while(!st.empty() && st.top()!='('){
                    ans += st.top();
                    st.pop();
                }
                if(!st.empty()){
                    st.pop();
                }
            }
            else{
                if(s[i]=='^'){
                    while(!st.empty() && priority[st.top()]>=priority[s[i]]){
                        ans += st.top();
                        st.pop();
                    }
                    st.push(s[i]);
                }
                else{
                    while(!st.empty() && priority[st.top()]>priority[s[i]]){
                        ans += st.top();
                        st.pop();
                    }
                    st.push(s[i]);
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