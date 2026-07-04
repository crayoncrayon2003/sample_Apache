# sample13_Mlib — MLlib (Machine Learning)

**MLlib** is one of Spark's four main parts.
It builds the whole flow — preprocessing, training, and evaluation — with a shared API:
`Transformer` / `Estimator` / `Pipeline`.

| File | What it does |
|---|---|
| `01_generateDummyTaxiData.py` | Generate 2000 dummy taxi rows for training. Adds a weak "longer distance -> more likely Card" signal so classification can learn something. |
| `02_regression.py` | **Regression** — predict `totalAmount` from `tripDistance` and more (LinearRegression, scored with RMSE / R2). |
| `03_classification.py` | **Classification** — predict whether the payment is Card (StringIndexer -> OneHotEncoder -> LogisticRegression, scored with Accuracy / F1). |

## Run

```bash
# First generate the training data
python3.12 01_generateDummyTaxiData.py

# Regression
python3.12 02_regression.py

# Classification
python3.12 03_classification.py
```

> MLlib needs no extra package — it runs with `pyspark` alone (see the repo-root [README.md](../README.md) for setup).

## Points

- **Pipeline**: line up preprocessing (like `VectorAssembler`) and the estimator, then run `fit` / `transform` in one go.
- **Feature vector**: Spark ML takes one `features` vector column, not many columns. `VectorAssembler` does that conversion.
- **Category conversion**: string categories go through two steps — `StringIndexer` (to numbers) then `OneHotEncoder` (to a vector).
- **Tuning**: `CrossValidator` + `ParamGridBuilder` do a grid search over `regParam` and `elasticNetParam` and keep the best model.
