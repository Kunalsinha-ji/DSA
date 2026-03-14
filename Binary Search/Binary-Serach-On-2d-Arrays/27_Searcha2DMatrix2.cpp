#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
    bool searchMatrix(vector<vector<int>>& matrix, int target) {
        int n = matrix.size();
        int m = matrix[0].size();

        for(int i=0;i<n;i++){
            if(matrix[i][0]<=target && matrix[i][m-1]>=target){
                int low = 0, high = m-1;

                while(low<=high){
                    int mid = low + (high-low)/2;

                    if(matrix[i][mid]==target){
                        return 1;
                    }
                    else if(matrix[i][mid]>target){
                        high = mid - 1;
                    }
                    else{
                        low = mid + 1;
                    }
                }
            }
        }
        return 0;
    }
};

// trick
/*
Intuition
The matrix has a special property:

Each row is sorted from left → right
Each column is sorted from top → bottom
Because of this ordering, we can eliminate either a row or a column in every step.
If we start from the top-right corner:

Everything left of it is smaller
Everything below it is larger
So the top-right element gives us a perfect decision point.
Think of it like walking down a staircase in the matrix:

Move left if the value is too big
Move down if the value is too small
This quickly shrinks the search space.
Approach
Start from the top-right corner of the matrix.
Compare the current element with the target.

Three possibilities:

✅ Equal to target → return true

⬅️ Target is smaller → move left (col--)

⬇️ Target is larger → move down (row++)

Why this works:

Moving left removes the current column.

Moving down removes the current row.

Thus, each step eliminates a portion of the matrix.

Complexity
Time complexity: O(M+N)

Space complexity: O(1)

*/
class Solution {
public:
    bool searchMatrix(vector<vector<int>>& matrix, int target) {
        int n = matrix.size();
        int row = 0;
        int col = matrix[0].size() - 1;
        while (row < matrix.size() && col >= 0) {
            if (target == matrix[row][col]) {
                return true;
            } else if (target < matrix[row][col]) {
                col--;       //move left
            } else {
                row++;      //move bottom
            }
        }
        return false;
    }
};
int main() {
    return 0;
}