#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
    void floydWarshall(int n, vector<vector<int>>& graph) {
        // Initialize distance matrix with graph values
        vector<vector<int>> dist = graph;
        // Floyd-Warshall algorithm
        for (int k = 0; k < n; ++k) {
            for (int i = 0; i < n; ++i) {
                for (int j = 0; j < n; ++j) {
                    if (dist[i][k] != INT_MAX && dist[k][j] != INT_MAX) {
                        dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j]);
                    }
                }
            }
        }
        // Update the original graph with shortest distances
        graph = dist;
    }
};

int main() {
    return 0;
}