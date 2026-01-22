#include <bits/stdc++.h>
using namespace std;

class Solution {
  public:
    vector<int> findUnion(vector<int>& a, vector<int>& b) {
        // code here
        unordered_map<int,int> mp;
        for(auto it: a){
            mp[it]++;
        }
        for(auto it: b){
            mp[it]++;
        }

        vector<int> v;
        for(auto it: mp){
            v.push_back(it.first);
        }
        return v;
    }
};

int main() {
    return 0;
}