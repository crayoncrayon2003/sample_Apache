import psycopg2

CONN = "host=localhost port=5432 dbname=postgres user=postgres password=password"


def main():
    conn = psycopg2.connect(CONN)
    conn.autocommit = True
    cur = conn.cursor()

    # Confirm MADlib is installed
    cur.execute("SELECT madlib.version();")
    print("MADlib:", cur.fetchone()[0])

    # Sample training data: y depends roughly linearly on x1, x2
    cur.execute("DROP TABLE IF EXISTS houses;")
    cur.execute("""
        CREATE TABLE houses (
            id    SERIAL PRIMARY KEY,
            size  INT,     -- x1: floor size
            rooms INT,     -- x2: number of rooms
            price INT      -- y : price
        );
    """)
    cur.execute("""
        INSERT INTO houses (size, rooms, price) VALUES
            (1000, 2, 200), (1500, 3, 320), (1800, 3, 360),
            (2400, 4, 480), (3000, 4, 600), (3500, 5, 710),
            (4000, 5, 800), (4500, 6, 910);
    """)

    # Train a linear regression model with MADlib (in-database).
    # linregr_train also creates a companion <output>_summary table, so drop both.
    cur.execute("DROP TABLE IF EXISTS houses_linregr, houses_linregr_summary;")
    cur.execute("""
        SELECT madlib.linregr_train(
            'houses',              -- source table
            'houses_linregr',      -- output model table
            'price',               -- dependent variable
            'ARRAY[1, size, rooms]'-- independent variables (1 = intercept)
        );
    """)

    # Inspect the trained coefficients
    cur.execute("SELECT coef, r2 FROM houses_linregr;")
    coef, r2 = cur.fetchone()
    print("coefficients [intercept, size, rooms]:", coef)
    print("R^2:", r2)

    cur.close()
    conn.close()


if __name__ == '__main__':
    main()
