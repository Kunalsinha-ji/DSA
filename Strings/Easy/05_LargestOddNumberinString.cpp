#include <bits/stdc++.h>
using namespace std;

// 2 * O(N)
class Solution {
public:
    string largestOddNumber(string num) {
        int n = num.size();
        int ind = -1;
        for(int i=n-1;i>=0;i--){
            if((num[i]-'0')%2){
                ind = i;
                break;
            }
        }
        if(ind==-1){
            return "";
        }
        return num.substr(0,ind+1);
    }
};

int main() {
    return 0;
}