#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
    vector<int> asteroidCollision(vector<int>& asteroids) {
        int n = asteroids.size();
        vector<int> ans;

        for(auto it: asteroids){
            if(it>0){
                ans.push_back(it);
            }
            else{
                while(ans.size()!=0 && ans.back()>0 && ans.back()<abs(it)){
                    ans.pop_back();
                }
                if(ans.size()==0 || ans.back()<0){
                    ans.push_back(it);
                }
                if(ans.back()==abs(it)){
                    ans.pop_back();
                }
            }
        }
        return ans;
    }
};

int main() {
    return 0;
}