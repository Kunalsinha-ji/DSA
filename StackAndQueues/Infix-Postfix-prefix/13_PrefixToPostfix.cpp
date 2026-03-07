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
    string preToPost(string s) {
        int n = s.size();
        stack<string> st;

        for(int i=n-1;i>=0;i--){
            if(isOperand(s[i])){
                string str = "";
                str += s[i];
                st.push(str);
            }
            else{
                string op1 = st.top();
                st.pop();
                string op2 = st.top();
                st.pop();

                string res = op1 + op2 + s[i];
                st.push(res);
            }
        }
        return st.top();
    }
};

int main() {
    return 0;
}