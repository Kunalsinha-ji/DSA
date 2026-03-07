#include <bits/stdc++.h>
using namespace std;

class Solution {
    static bool cmp(pair<int,char> &p1,pair<int,char> &p2){
        if(p1.first==p2.first){
            return p1.second<p2.second;
        }
        return p1.first>p2.first;
    }
public:
    string frequencySort(string s) {
        unordered_map<char,int> freq;
        vector<pair<int,char>> arr;

        for(auto it: s){
            freq[it]++;
        }
        for(auto it: freq){
            arr.push_back({it.second,it.first});
        }

        sort(arr.begin(),arr.end(),cmp);
        string ans = "";
        for(auto it: arr){
            string k(it.first,it.second);
            ans += k;
        }
        return ans;
    }
};

class Solution {
public:
    string frequencySort(string s) {
        unordered_map<char,int> mp;
        multimap<int,char> r;
        string ans="";

        for(auto a : s)
            mp[a]++;

        for(auto a : mp)
            r.insert({a.second, a.first});

        for(auto it = r.rbegin(); it != r.rend(); ++it)
            ans += string(it->first, it->second);

        return ans;
    }
};

int main() {
    return 0;
}