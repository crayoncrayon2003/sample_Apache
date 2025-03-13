package com.example;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.kafka.connect.connector.ConnectRecord;
import org.apache.kafka.connect.transforms.Transformation;
import org.apache.kafka.common.config.ConfigDef;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class CustomTransform<R extends ConnectRecord<R>> implements Transformation<R> {

    private static final Logger logger = LoggerFactory.getLogger(CustomTransform.class);
    private static final ObjectMapper objectMapper = new ObjectMapper(); // JSON シリアライズ用

    @Override
    public R apply(R record) {
        logger.info("Original Record: {}", record.value());

        Map<String, Object> value;
        if (record.value() instanceof String) {
            try {
                value = objectMapper.readValue((String) record.value(), Map.class);
            } catch (Exception e) {
                logger.error("Failed to parse record value as JSON: {}", record.value(), e);
                return record;
            }
        } else if (record.value() instanceof Map) {
            value = (Map<String, Object>) record.value();
        } else {
            logger.warn("Skipping record with unexpected value type: {}", record.value().getClass());
            return record;
        }

        Map<String, Object> transformedValue = new HashMap<>();

        Map<String, Object> data = (Map<String, Object>) value.get("data");
        if (data == null) {
            logger.error("Missing 'data' field in the record");
            return record;
        }

        List<Map<String, Object>> records = (List<Map<String, Object>>) data.get("records");
        List<Map<String, Object>> fields = (List<Map<String, Object>>) data.get("fields");

        if (records == null || fields == null) {
            logger.error("Missing 'records' or 'fields' in the 'data' field");
            return record;
        }

        Map<String, String> fieldTypes = new HashMap<>();
        for (Map<String, Object> field : fields) {
            String fieldId = (String) field.get("id");
            String fieldType = (String) field.get("type");
            fieldTypes.put(fieldId, fieldType);
        }
     
        for (Map<String, Object> recordEntry : records) {
            for (Map.Entry<String, Object> entry : recordEntry.entrySet()) {
                String key = entry.getKey();
                Object valueObj = entry.getValue();

                String type = fieldTypes.get(key);
                if (type == null) {
                    logger.warn("No type information for key: {}", key);
                    continue;
                }

                Map<String, Object> fieldInfo = new HashMap<>();
                fieldInfo.put("value", valueObj);
                fieldInfo.put("type", type);

                transformedValue.put(key, fieldInfo);
            }
        }

        String serializedValue;
        try {
            serializedValue = objectMapper.writeValueAsString(transformedValue);
        } catch (Exception e) {
            logger.error("Failed to serialize transformed value as JSON: {}", transformedValue, e);
            return record;
        }

        logger.info("Serialized Transformed Record: {}", serializedValue);

        return record.newRecord(record.topic(), record.kafkaPartition(),
                record.keySchema(), record.key(),
                record.valueSchema(), serializedValue,
                record.timestamp());
    }

    @Override
    public ConfigDef config() {
        return new ConfigDef();
    }

    @Override
    public void configure(Map<String, ?> configs) {
        logger.info("CustomTransform configured.");
    }

    @Override
    public void close() {
        logger.info("CustomTransform closed and resources cleared.");
    }
}
