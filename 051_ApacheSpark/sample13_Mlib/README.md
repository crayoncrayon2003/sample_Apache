# sample13_Mlib — MLlib (Machine Learning)

**MLlib** is one of Spark's four main parts.
It builds the whole flow — preprocessing, training, and evaluation — with a shared API:
`Transformer` / `Estimator` / `Pipeline`.

| File | What it does |
|---|---|
| `01_generateDummyTaxiData.py` | Generate 2000 dummy taxi rows for training. Adds a weak "longer distance -> more likely Card" signal so classification can learn something. |
| `02_regression.py` | **Regression** — predict `totalAmount` from `tripDistance` and more (LinearRegression, scored with RMSE / R2). |
| `03_classification.py` | **Classification** — predict whether the payment is Card (StringIndexer -> OneHotEncoder -> LogisticRegression, scored with Accuracy / F1). |
| `04_clustering.py` | **Clustering** — group rides with KMeans (unsupervised), scored with the silhouette score. |
| `05_encoder.py` | **Encoding** — turn the `paymentType` category into a vector step by step (StringIndexer -> OneHotEncoder), printing the DataFrame before and after each stage. |
| `06_scaling.py` | **Feature prep** — standardize numeric features with StandardScaler, then reduce dimensions with PCA, showing the DataFrame before and after. |

## Run

```bash
# First generate the training data
python3.12 01_generateDummyTaxiData.py

# Regression
python3.12 02_regression.py

# Classification
python3.12 03_classification.py

# Clustering
python3.12 04_clustering.py

# Feature engineering (encoding, scaling / PCA)
python3.12 05_encoder.py
python3.12 06_scaling.py
```

> MLlib needs no extra package — it runs with `pyspark` alone (see the repo-root [README.md](../README.md) for setup).

## Points

- **Pipeline**: line up preprocessing (like `VectorAssembler`) and the estimator, then run `fit` / `transform` in one go.
- **Feature vector**: Spark ML takes one `features` vector column, not many columns. `VectorAssembler` does that conversion.
- **Category conversion**: string categories go through two steps — `StringIndexer` (to numbers) then `OneHotEncoder` (to a vector). `05_encoder.py` shows the DataFrame at each step.
- **Feature prep**: `StandardScaler` puts numeric features on the same scale; `PCA` cuts down the number of dimensions.
- **Tuning**: `CrossValidator` + `ParamGridBuilder` do a grid search over `regParam` and `elasticNetParam` and keep the best model.
