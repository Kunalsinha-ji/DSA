#include <bits/stdc++.h>
using namespace std;

// Brute force
class Solution {
    bool isPalindrome(string str){
        int i=0;
        int j=str.size()-1;

        while(i<j){
            if(str[i]!=str[j]){
                return false;
            }
            i++;
            j--;
        }
        return true;
    }
public:
    string longestPalindrome(string s) {
        int n = s.size();
        string ans = "";
        for(int i=0;i<n;i++){
            string str = "";
            for(int j=i;j<n;j++){
                str += s[j];
                if(str.size()>ans.size() && isPalindrome(str)){
                    ans = str;
                }
            }
        }
        return ans;
    }
};

// Better using 2 pointers and adding up the palindrome
class Solution {
    string solve(string &s,int i,int j){
        string res = "";

        while(i>=0 && j<s.size()){
            if(s[i]==s[j]){
                if(i==j){
                    res += s[i];
                }
                else{
                    res = s[i] + res + s[j];
                }
            }
            else{
                break;
            }
            i--;
            j++;
        }
        return res;
    }
public:
    string longestPalindrome(string s) {
        string ans = "";
        int n = s.size();

        for(int i=0;i<n;i++){
            string op1 = solve(s,i,i);
            string op2 = solve(s,i,i+1);

            string k;
            if(op1.size()>op2.size()){
                k = op1;
            }
            else{
                k = op2;
            }

            if(ans.size()<k.size()){
                ans = k;
            }
        }
        return ans;
    }
};

int main() {
    return 0;
}