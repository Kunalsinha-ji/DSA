#include <bits/stdc++.h>
using namespace std;

class Solution {
  public:
    vector<int> findUnion(vector<int> &a, vector<int> &b) {
        vector<int> ans;
        int i = 0,j = 0;
        int n = a.size(), m = b.size();

        while(i<n && j<m){
            int element = -1;
            if(a[i]==b[j]){
                element = a[i];
                i++;j++;
            }
            else if(a[i]<b[j]){
                element = a[i];
                i++;
            }
            else{
                element = b[j];
                j++;
            }
            if(ans.size()==0 || ans.back()!=element){
                ans.push_back(element);
            }
        }

        while(i<n){
            if(ans.size()==0 || ans.back()!=a[i]){
                ans.push_back(a[i]);
            }
            i++;
        }
        while(j<m){
            if(ans.size()==0 || ans.back()!=b[j]){
                ans.push_back(b[j]);
            }
            j++;
        }
        return ans;
    }
};

int main() {
    return 0;
}