#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
    bool lemonadeChange(vector<int>& bills) {
        int ten = 0;
        int five = 0;

        for(auto it: bills){
            if(it==5){
                five++;
            }
            else if(it==10){
                if(five){
                    five--;
                    ten++;
                }
                else{
                    return false;
                }
            }
            else{
                if(ten && five){
                    ten--;
                    five--;
                }
                else if(five>=3){
                    five -= 3;
                }
                else{
                    return false;
                }
            }
        }
        return true;
    }
};

int main() {
    return 0;
}