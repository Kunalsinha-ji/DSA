#include <bits/stdc++.h>
using namespace std;

// Brute force - 2* (n log n) + n
class Solution {
public:
    bool isAnagram(string s, string t) {
        int n = s.size(),m = t.size();
        if(n!=m){
            return false;
        }
        sort(s.begin(),s.end());
        sort(t.begin(),t.end());

        for(int i=0;i<n;i++){
            if(s[i]!=t[i]){
                return false;
            }
        }
        return true;
    }
};

// Optimal 2* O(N) + O(k). k is size of map at most
class Solution {
public:
    bool isAnagram(string s, string t) {
        int n = s.size(),m = t.size();
        if(n!=m){
            return false;
        }

        unordered_map<char,int> mp;
        for(int i=0;i<n;i++){
            mp[s[i]]++;
        }
        for(int i=0;i<m;i++){
            mp[t[i]]--;
        }

        for(auto it: mp){
            if(it.second)   return false;
        }
        return true;
    }
};

// Note unordered_map can have some time complexity therefore we can use array instead
class Solution {
public:
    bool isAnagram(string s, string t) {
        int n = s.size(),m = t.size();
        if(n!=m){
            return false;
        }

        vector<int> mp(26,0);
        for(int i=0;i<n;i++){
            mp[s[i]-'a']++;
        }
        for(int i=0;i<m;i++){
            mp[t[i]-'a']--;
        }

        for(auto it: mp){
            if(it)   return false;
        }
        return true;
    }
};

int main() {
    return 0;
}