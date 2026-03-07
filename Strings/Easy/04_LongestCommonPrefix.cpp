#include <bits/stdc++.h>
using namespace std;

// O(N*N)
class Solution {
public:
    string longestCommonPrefix(vector<string>& strs) {
        string ans = strs[0];

        for(int i=1;i<strs.size();i++){
            int size = 0;
            for(int j=0;j<min(ans.size(),strs[i].size());j++){
                if(ans[j]!=strs[i][j]){
                    break;
                }
                size++;
            }
            if(size==0){
                return "";
            }
            ans = ans.substr(0,size);
        }
        return ans;
    }
};

int main() {
    return 0;
}