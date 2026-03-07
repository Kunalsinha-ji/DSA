#include <bits/stdc++.h>
using namespace std;

// O(n) + O(n) at best can also go to O(N*N)
class Solution {
public:
    bool rotateString(string s, string goal) {
        int n = s.size(), m = goal.size();
        if(n!=m)    return false;

        for(int i=0;i<n;i++){
            if(goal[0]==s[i]){
                string s1 = s.substr(i,n);
                string s2 = s.substr(0,i);
                if(s1 + s2==goal){
                    return true;
                }
            }
        }

        return false;
    }
};

int main() {
    return 0;
}