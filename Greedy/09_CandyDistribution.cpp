#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
    int candy(vector<int>& ratings) {
        int n = ratings.size();
        int totalCandies = 0;

        // candyCount[i] will store the number of candies given to the i-th child
        vector<int> candyCount(n);

        // First child always gets at least one candy
        candyCount[0] = 1;

        // LEFT TO RIGHT PASS
        // If the current child has a higher rating than the previous child,
        // give one more candy than the previous child.
        for(int i = 1; i < n; i++){
            if(ratings[i] > ratings[i - 1]){
                candyCount[i] = candyCount[i - 1] + 1;
            }
            else{
                // Otherwise give minimum one candy
                candyCount[i] = 1;
            }
        }

        // Start total with last child's candies
        totalCandies += candyCount[n - 1];

        // RIGHT TO LEFT PASS
        // Ensure the right neighbor condition is also satisfied
        for(int i = n - 2; i >= 0; i--){
            // If current child has higher rating than next child
            // they should get more candies than the next child
            if(ratings[i] > ratings[i + 1]){
                candyCount[i] = max(candyCount[i], candyCount[i + 1] + 1);
            }
            else{
                // Keep the current value (at least 1)
                candyCount[i] = max(candyCount[i], 1);
            }

            // Add candies to total
            totalCandies += candyCount[i];
        }

        return totalCandies;
    }
};

int main() {
    return 0;
}