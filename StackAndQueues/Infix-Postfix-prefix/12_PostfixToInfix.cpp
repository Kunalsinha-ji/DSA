#include <bits/stdc++.h>
using namespace std;

// User function Template for C++

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
    string postToInfix(string &s) {
        stack<string> st;

        for(auto it: s){
            if(isOperand(it)){
                string str = "";
                str += it;
                st.push(str);
            }
            else{
                string op2 = st.top();
                st.pop();
                string op1 = st.top();
                st.pop();

                string res = "(" + op1 + it + op2 + ')';
                st.push(res);
            }
        }
        return st.top();
    }
};

int main() {
    return 0;
}