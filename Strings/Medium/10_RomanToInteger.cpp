#include <bits/stdc++.h>
using namespace std;

// using array
class Solution {
public:
    int romanToInt(string s) {
        int n = s.size();
        int ans = 0;
        vector<int> mp(26);
        mp['I' - 'A'] = 1;
        mp['V' - 'A'] = 5;
        mp['X' - 'A'] = 10;
        mp['L' - 'A'] = 50;
        mp['C' - 'A'] = 100;
        mp['D' - 'A'] = 500;
        mp['M' - 'A'] = 1000;

        for(int i=n-1;i>=0;i--){
            if(i==n-1){
                ans += mp[ s[i] - 'A'];
                continue;
            }
            int num = mp[ s[i] - 'A'];
            int prev = mp[ s[i+1] - 'A'];

            if(prev>num){
                ans -= num;
            }
            else{
                ans += num;
            }
        }
        return ans;
    }
};

// Using map
class Solution {
public:
    int romanToInt(string s) {
        int n = s.size();
        int ans = 0;
        unordered_map<char,int> mp;
        mp['I'] = 1;
        mp['V'] = 5;
        mp['X'] = 10;
        mp['L'] = 50;
        mp['C'] = 100;
        mp['D'] = 500;
        mp['M'] = 1000;

        for(int i=n-1;i>=0;i--){
            if(i==n-1){
                ans += mp[s[i]];
                continue;
            }
            int num = mp[s[i]];
            int prev = mp[s[i+1]];

            if(prev>num){
                ans -= num;
            }
            else{
                ans += num;
            }
        }
        return ans;
    }
};

int main() {
    return 0;
}