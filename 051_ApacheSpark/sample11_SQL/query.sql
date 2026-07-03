SELECT
    CONCAT('urn:ngsi-ld:', `key1`) AS id,
    'test' AS type,
    STRUCT(`key1` AS value, 'Text' AS type) AS data1,
    STRUCT(`key2` AS value, 'Text' AS type) AS data2,
    STRUCT(`key3` AS value, 'Text' AS type) AS data3
FROM recode;
