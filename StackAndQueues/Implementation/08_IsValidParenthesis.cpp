#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
    bool isValid(string s) {
        int n = s.size();
        if(n==0){
            return true;
        }
        if(n%2==1){
            return false;
        }

        stack<char> st;

        for(auto it: s){
            if(it=='(' || it=='[' || it=='{'){
                st.push(it);
            }
            else{
                if(st.empty()){
                    return false;
                }
                if(it==')'){
                    char ch = st.top();
                    st.pop();
                    if(ch!='(') return false;
                }
                else if(it==']'){
                    char ch = st.top();
                    st.pop();
                    if(ch!='[') return false;
                }
                else{
                    char ch = st.top();
                    st.pop();
                    if(ch!='{') return false;
                }
            }
        }
        if(st.empty())  return true;
        return false;
    }
};

int main() {
    return 0;
}