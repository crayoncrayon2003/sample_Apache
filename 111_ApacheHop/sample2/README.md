# pre process
```
./00_mkdir.sh
```

# build and run
```
docker compose up -d
```
Access the following URL using the Web browser.
* http://localhost:8082/ui

# How to use
## Create Workflow
Do one of the following, and select Workflow.
* Click on the "+" icon at the top of the screen.
* Press "CTRL + N".
## Create Pipeline
Do one of the following, and select Pipeline.
* Click on the "+" icon at the top of the screen.
* Press "CTRL + N".

## Case1 : CSV input
### Step1 : Create Pipeline
1. Click on the "+" icon at the top of the screen, and select Pipeline.

### Step2 : CSV input
1. Click on the Field. Search for "CSV file input"
2. Click on the text of "CSV file input".
・Transform name             ： CSV file input
・Filename		               ： ${PROJECT_HOME}/data.csv
・Delimiter		               ： ,
・Enclosure		               ： "
・NIO buffer size            ： 50000
・Laz conversion	           ： on
・Header row present         ： on
・Add filename to result     ： off
・The row number feild name	 ： (blank)
・Running in parallel    	   ： off
・New line possible in feild ： off
・File encoding              ： UTF-8
・Schema feffinition         ： (blank)
3. Click on the "Get Fields"

### Step3 : Table output
1. Click on the Field. Search for "Table output"
2. Click on the text of "Table output".
3. Setting following.
・Transform name         : Table output
・Connection             : *1
・Target schema          : main
・Target table           : csvtable
・Commit size            : 1000
・Truncate table         : off
・Truncate on first row  : on
・Ignore insert errors   : off
・Specify database fiels : on

*1 Relational Database Connection
Click on the "+" icon at "Create a new metadata elemnt".

・Connection name	     : duckdb_writer

Tab of "General"
・Connection type        : DuckDB
・Installed driver       : org.duckdb.DuckDBDriver
・Username		           : (blank)
・Password		           : (blank)
・Server host name       : (blank)
・Post number            : (blank)
・Database name          : ${PROJECT_HOME}/duckdb.db
・Manual conection url   : (blank)

Tab of "Advanced"
・Supports the Boolean data type             : on
・Supports the Timestamp data type           : on
・Quote all indentiffiers in database        : off
・Force all indentiffiers to lower case      : off
・Force all indentiffiers to upper case      : off
・Preserve case of reserved word             : off
・preferred shema name                       : (blank)
・The SQL statements to run after connecting : following

CREATE TABLE IF NOT EXISTS csvtable (
  name VARCHAR,
  address VARCHAR,
  num DOUBLE,
  lon DOUBLE,
  lat DOUBLE
);

Tab of "Option"
・default

4. tab of "Main options"
・Partation data over tabels               : off
・Patitioning field                        : (blank)
・Patition data per month                  : on
・Patition data per day                    : off
・Use batch update for inserts             : off
・Is the name of table defiend in a fields : off
・Field that contatins name of table       : (blank)
・Store the tablename field                : on
・Return auto-generated key                : off
・Name of auto-genetated key field         : (blank)

5. tab of "Database fields"
Click on the "Get Fields"

### Step4 : Table input
1. Click on the Field. Search for "Table input"
2. Click on the text of "Table input".
3. Setting following.
・Transform name         : Table input
・Connection             : *2
・SQL                    : following

SELECT
  CONCAT('urn:ngsi-ld:test:', LPAD(CAST(ROW_NUMBER() OVER (ORDER BY name) AS VARCHAR), 3, '0')) AS id,
  'test' AS type,
  JSON_OBJECT('type', 'Text', 'value', name    ) AS name,
  JSON_OBJECT('type', 'Text', 'value', address ) AS address,
  JSON_OBJECT('type', 'Text', 'value', num     ) AS num,
  JSON_OBJECT('type', 'Text', 'value', lon     ) AS lon,
  JSON_OBJECT('type', 'Text', 'value', lat     ) AS lat
FROM csvtable;

*2 Relational Database Connection
Click on the "+" icon at "Create a new metadata elemnt".

・Connection name	     : duckdb_reader

Tab of "General"
・Connection type        : DuckDB
・Installed driver       : org.duckdb.DuckDBDriver
・Username		           : (blank)
・Password		           : (blank)
・Server host name       : (blank)
・Post number            : (blank)
・Database name          : ${PROJECT_HOME}/duckdb.db
・Manual conection url   : (blank)

Tab of "Advanced"
・Supports the Boolean data type             : on
・Supports the Timestamp data type           : on
・Quote all indentiffiers in database        : off
・Force all indentiffiers to lower case      : off
・Force all indentiffiers to upper case      : off
・Preserve case of reserved word             : off
・preferred shema name                       : (blank)
・The SQL statements to run after connecting : (blank)

Tab of "Option"
・default

### Step5 : Enhanced JSON output
・Transform name              : Enhanced JSON Output

Tab of "General"
・Transform name              : Write to file
・Json block name             : result
・Output Value                : outputValue
・Foce arrays in JSON         : off
・Foce single grouped Item    : off
・Pretty Pring Json           : off
・Filennmae　　　　　　　　　　: ${PROJECT_HOME}/output/filename
・Append                      : off
・Nr rows in a block          : 0
・Create Parent folder        : on
・Do not open create at start : off
・Extentions                  : json
・Encoding                    : UTF-8
・Include data in filename    : off
・Include time in filename    : off
・Add File to result filenames: off

Tab of "Grope Key"
default

Tab of "Fields"
・Fieldname : Element name : Json Fragment : Remove Element name : Remove if Blank
・id        : id           : N             : N                   : N
・type      : type         : N             : N                   : N
・name    　: name         : Y             : N                   : N
・address   : address      : Y             : N                   : N
・num       : num          : Y             : N                   : N
・lon       : latitude     : Y             : N                   : N
・lat       : longitude    : Y             : N                   : N

Tab of "Additinal output fields"
default


# down
```
docker compose down
```

# post process
```
./00_mkdir.sh
```

