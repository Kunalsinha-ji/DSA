#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
    int myAtoi(string s) {
        int i = 0;
        bool neg = 0;
        long ans = 0;

        while(i<s.size()){
            if(s[i]==' '){
                i++;
                continue;
            }
            if(s[i]=='-'){
                neg = 1;
                i++;
            }
            else if(s[i]=='+'){
                i++;
            }
            while(i<s.size() && s[i]>='0' && s[i]<='9'){
                ans = ans *10 + (s[i]-'0');
                if(ans>INT_MAX){
                    return neg==0 ? INT_MAX : INT_MIN;
                }
                i++;
            }
            return neg == 0 ? ans : -ans;
        }
        return ans;
    }
};

int main() {
    return 0;
}