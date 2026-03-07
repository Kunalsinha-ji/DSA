#include <bits/stdc++.h>
using namespace std;

// brute force
class Solution {
public:
    bool isIsomorphic(string s, string t) {
        int n = s.size(), m = t.size();
        if(n!=m)    return false;

        unordered_map<char,char> m1,m2;
        for(int i=0;i<n;i++){
            if(m1.find(s[i])!=m1.end() && m2.find(t[i])==m2.end()){
                return false;
            }
            else if(m1.find(s[i])==m1.end() && m2.find(t[i])!=m2.end()){
                return false;
            }
            else if(m1.find(s[i])!=m1.end()){
                if(m1[s[i]]!=t[i]){
                    return false;
                }
                if(m2[t[i]]!=s[i]){
                    return false;
                }
            }
            else{
                m1[s[i]] = t[i];
                m2[t[i]] = s[i];
            }
        }
        return true;
    }
};

// optimal - use array just put index + 1 for each item and
// while iteration if the frequency of corresponding mapped items are not equal return false
class Solution {
public:
    bool isIsomorphic(string s, string t) {
        int n = s.size(), m = t.size();
        vector<int> m1(256,0), m2(256,0);

        for(int i=0;i<n;i++){
            if(m1[s[i]]!=m2[t[i]]){
                return false;
            }

            m1[s[i]] = i+1;
            m2[t[i]] = i+1;
        }
        return true;
    }
};

int main() {
    return 0;
}