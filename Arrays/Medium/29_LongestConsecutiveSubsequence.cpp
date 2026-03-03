#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
    int longestConsecutive(vector<int>& nums) {
        int ans = 0;
        unordered_set<int> st(nums.begin(),nums.end());

        for(auto it: st){
            int num = it;
            if(st.find(it-1)!=st.end()){
                continue;
            }
            else{
                int len = 0;
                int x = it;
                while(st.find(x)!=st.end()){
                    len++;
                    x++;
                }
                ans = max(ans,len);
            }
        }
        return ans;
    }
};

int main() {
    return 0;
}