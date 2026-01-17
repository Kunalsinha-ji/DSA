#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
    bool lemonadeChange(vector<int>& bills) {
        int f = 0,t = 0;

        int i=0;
        while(i<bills.size()){
            if(bills[i]==5){
                f++;
            }
            else if(bills[i]==10){
                if(f){
                    f--;
                    t++;
                }
                else{
                    return 0;
                }
            }
            else{
                if(t && f){
                    t--;
                    f--;
                }
                else if(f>=3){
                    f -= 3;
                }
                else{
                    return 0;
                }
            }
            i++;
        }
        return 1;
    }
};

int main() {
    return 0;
}