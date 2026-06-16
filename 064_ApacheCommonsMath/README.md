# about
Apache Commons Math is a pure Java statistics / numerics library (no database).
This sample computes descriptive statistics, a linear regression and a t-test.

# build and run
```bash
mvn -q compile exec:java
```

# alternatively
```bash
mvn -q package
java -cp target/classes:$(find ~/.m2 -name 'commons-math3-3.6.1.jar') Sample1
```
