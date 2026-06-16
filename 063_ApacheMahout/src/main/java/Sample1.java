import org.apache.mahout.math.DenseMatrix;
import org.apache.mahout.math.DenseVector;
import org.apache.mahout.math.Matrix;
import org.apache.mahout.math.Vector;
import org.apache.mahout.math.stats.OnlineSummarizer;

public class Sample1 {

    public static void main(String[] args) {
        // In-core distributed linear-algebra primitives (Mahout "Samsara" math)
        double[][] raw = {
            {10, 10}, {13, 10}, {14, 11}, {11, 11}, {14, 13},
            {15, 15}, {16, 13}, {14, 14}, {11, 16}, {9, 15}
        };
        Matrix m = new DenseMatrix(raw); // rows = samples, cols = [temperature, humidity]

        // 1) Column means via matrix/vector algebra
        Vector ones = new DenseVector(m.numRows()).assign(1.0);
        Vector colSums = m.transpose().times(ones);
        Vector colMeans = colSums.divide(m.numRows());
        System.out.println("== Column means (temperature, humidity) ==");
        System.out.println(colMeans);

        // 2) Streaming summary statistics (mean, sd, quartiles) for temperature
        OnlineSummarizer summ = new OnlineSummarizer();
        for (int r = 0; r < m.numRows(); r++) {
            summ.add(m.get(r, 0));
        }
        System.out.println();
        System.out.println("== Summary statistics (temperature) ==");
        System.out.printf("mean   : %.3f%n", summ.getMean());
        System.out.printf("stddev : %.3f%n", summ.getSD());
        System.out.printf("min    : %.1f%n", summ.getMin());
        System.out.printf("q1     : %.3f%n", summ.getQuartile(1));
        System.out.printf("median : %.3f%n", summ.getMedian());
        System.out.printf("q3     : %.3f%n", summ.getQuartile(3));
        System.out.printf("max    : %.1f%n", summ.getMax());
    }
}
