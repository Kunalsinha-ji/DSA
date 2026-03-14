#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
    int findContentChildren(vector<int>& g, vector<int>& s) {
        sort(g.begin(),g.end());
        sort(s.begin(),s.end());

        // s[i] is size of cookie and g[i] is greed factor

        int i = 0,j=0;

        while(j<s.size() && i<g.size()){
            if(g[i]>s[j]){
                j++;
            }
            else{
                j++;i++;
            }
        }
        return i;
    }
};

int main() {
    return 0;
}