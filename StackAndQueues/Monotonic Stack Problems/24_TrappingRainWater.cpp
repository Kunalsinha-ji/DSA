#include <bits/stdc++.h>
using namespace std;

class Solution {

    // Function to compute the maximum height to the right of each index
    vector<int> computeRightMaxHeights(vector<int> &heights){
        int n = heights.size();
        vector<int> rightMax(n, 0);

        int maxHeightFromRight = 0;

        // Traverse from right to left
        for(int i = n - 1; i >= 0; i--){
            maxHeightFromRight = max(maxHeightFromRight, heights[i]);
            rightMax[i] = maxHeightFromRight;
        }

        return rightMax;
    }

public:
    int trap(vector<int>& heights) {
        int n = heights.size();

        // Array to store maximum height to the left of each index
        vector<int> leftMax(n, 0);

        // Array to store maximum height to the right of each index
        vector<int> rightMax = computeRightMaxHeights(heights);

        int maxHeightFromLeft = 0;
        int totalWaterTrapped = 0;

        for(int i = 0; i < n; i++){

            // Update maximum height from the left
            maxHeightFromLeft = max(maxHeightFromLeft, heights[i]);
            leftMax[i] = maxHeightFromLeft;

            int waterAtCurrentIndex = min(leftMax[i], rightMax[i]) - heights[i];

            totalWaterTrapped += waterAtCurrentIndex;
        }

        return totalWaterTrapped;
    }
};

int main() {
    return 0;
}