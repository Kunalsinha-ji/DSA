#include <bits/stdc++.h>
using namespace std;

// Brute force
class Solution {
public:
    string reverseWords(string s) {
        while(s.size() && s.back()==' '){
            s.pop_back();
        }
        reverse(s.begin(),s.end());
        while(s.size() && s.back()==' '){
            s.pop_back();
        }

        string ans = "";
        string temp = "";

        for(int i=0;i<s.size();i++){
            if(s[i]==' '){
                if(temp!=""){
                    reverse(temp.begin(),temp.end());
                    ans += temp + " ";
                    temp = "";
                }
            }
            else{
                temp += s[i];
            }
        }
        reverse(temp.begin(),temp.end());
        ans += temp;
        return ans;
    }
};

// Optimal -> stack and O(N)
class Solution {
public:
    string reverseWords(string s) {
        string ans = "";
        stack<string> st;
        string temp = "";

        for(int i=0;i<s.size();i++){
            if(s[i]==' '){
                if(temp!=""){
                    st.push(temp);
                }
                temp = "";
            }
            else{
                temp += s[i];
            }
        }
        if(temp!=""){
            st.push(temp);
            temp = "";
        }
        while(!st.empty()){
            ans += st.top() + " ";
            st.pop();
        }
        if(ans==""){
            return "";
        }
        ans.pop_back();
        return ans;
    }
};


int main() {
    return 0;
}