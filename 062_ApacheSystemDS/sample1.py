import numpy as np
from systemds.context import SystemDSContext
from systemds.operator.algorithm import lm

# Apache SystemDS: declarative statistics / ML. Runs on an embedded Java runtime
# (no external database). Here we compute column means and fit a linear model.


def main():
    # Sample data: y depends roughly linearly on x1, x2
    X = np.array([
        [1000, 2], [1500, 3], [1800, 3], [2400, 4],
        [3000, 4], [3500, 5], [4000, 5], [4500, 6],
    ], dtype=np.float64)
    y = np.array([[200], [320], [360], [480], [600], [710], [800], [910]], dtype=np.float64)

    with SystemDSContext() as sds:
        mX = sds.from_numpy(X)
        mY = sds.from_numpy(y)

        # Column means (declarative aggregation)
        col_means = mX.mean(axis=0).compute()
        print("column means [size, rooms]:", col_means)

        # Fit a linear regression model: weights for each feature
        weights = lm(mX, mY).compute()
        print("linear model weights:\n", weights)


if __name__ == '__main__':
    main()
