SELECT
    'urn:ngsi-ld:' || COALESCE(CAST(key1 AS VARCHAR), 'null') AS id,
    'test' AS type,
    json_object('value', COALESCE(key1, NULL), 'type', 'Text') AS data1,
    json_object('value', COALESCE(key2, NULL), 'type', 'Text') AS data2,
    json_object('value', COALESCE(key3, NULL), 'type', 'Text') AS data3
FROM arrow_table;
