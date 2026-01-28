#include <bits/stdc++.h>
using namespace std;

class Solution {
    double solve(double x,int n){
        if(n==0){
            return 1.0;
        }
        if(n==1){
            return x;
        }

        double res = solve(x,n/2);
        if(n%2){
            return res*res*x;
        }
        else{
            return res*res;
        }
    }
public:
    double myPow(double x, int n) {
        int sign = 1;
        if(n<0){
            sign = -1;
        }

        return sign==1? solve(x,n) : 1/solve(x,n);
    }
};

int main() {
    return 0;
}