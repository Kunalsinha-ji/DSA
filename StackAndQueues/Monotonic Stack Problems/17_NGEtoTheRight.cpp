#include <bits/stdc++.h>
using namespace std;

class Solution {
  public:

    vector<int> count_NGE(vector<int> &arr, vector<int> &indices) {
        vector<int> ans;
        for(auto i : indices){
            int ele = arr[i];
            int count = 0;
            for(int j=i+1;j<arr.size();j++){
                if(arr[j]>ele){
                    count++;
                }
            }
            ans.push_back(count);
        }
        return ans;
    }
};

int main() {
    return 0;
}