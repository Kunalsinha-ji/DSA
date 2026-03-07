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
    string postToPre(string s) {
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

                string res = it + op1 + op2;
                st.push(res);
            }
        }
        return st.top();
    }
};

int main() {
    return 0;
}