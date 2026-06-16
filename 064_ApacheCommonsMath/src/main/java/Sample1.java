import org.apache.commons.math3.stat.descriptive.DescriptiveStatistics;
import org.apache.commons.math3.stat.regression.SimpleRegression;
import org.apache.commons.math3.stat.inference.TTest;

public class Sample1 {

    public static void main(String[] args) {
        // Sample data: temperature readings from a sensor
        double[] temperature = {10, 13, 14, 11, 14, 15, 16, 14, 11, 9};
        double[] humidity    = {10, 10, 11, 11, 13, 15, 13, 14, 16, 15};

        // 1) Descriptive statistics
        DescriptiveStatistics stats = new DescriptiveStatistics();
        for (double t : temperature) {
            stats.addValue(t);
        }
        System.out.println("== Descriptive statistics (temperature) ==");
        System.out.printf("n        : %d%n", stats.getN());
        System.out.printf("mean     : %.3f%n", stats.getMean());
        System.out.printf("stddev   : %.3f%n", stats.getStandardDeviation());
        System.out.printf("min/max  : %.1f / %.1f%n", stats.getMin(), stats.getMax());
        System.out.printf("median   : %.3f%n", stats.getPercentile(50));

        // 2) Simple linear regression: temperature ~ humidity
        SimpleRegression reg = new SimpleRegression();
        for (int i = 0; i < temperature.length; i++) {
            reg.addData(humidity[i], temperature[i]);
        }
        System.out.println();
        System.out.println("== Linear regression (temperature ~ humidity) ==");
        System.out.printf("intercept: %.4f%n", reg.getIntercept());
        System.out.printf("slope    : %.4f%n", reg.getSlope());
        System.out.printf("R^2      : %.4f%n", reg.getRSquare());

        // 3) Hypothesis test: paired t-test between the two series
        System.out.println();
        System.out.println("== Paired t-test (temperature vs humidity) ==");
        TTest tTest = new TTest();
        System.out.printf("t-statistic : %.4f%n", tTest.pairedT(temperature, humidity));
        System.out.printf("p-value     : %.4f%n", tTest.pairedTTest(temperature, humidity));
    }
}
