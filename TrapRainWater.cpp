/*
 * Given n non-negative integers representing an elevation map where the width of each bar is 1, compute how much water it can trap after raining.
 * Input: height = [0,1,0,2,1,0,1,3,2,1,2,1]
 * Output: 6
 */

class Solution {
public:
    int trap(vector<int>& h) {
        int i = 0, j = h.size() - 1, leftM = 0, rightM = 0, res = 0;
        while(i <= j) {
            if (leftM <= rightM) {
                leftM = max(leftM, h[i]);
                res += leftM - h[i];
                i++;
            } else {
                rightM = max(rightM, h[j]);
                res += rightM - h[j];
                j--;
            }
        }
        return res;
    }
};

int main() {
	Solution s;
	vector<int> nums = {0,1,0,2,1,0,1,3,2,1,2,1};
	int n = s.trap(nums);
	cout << "Max Water that can be trapped : " << n;
	return 0;
}

