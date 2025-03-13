package com.example;

import org.apache.kafka.connect.connector.Task;
import org.apache.kafka.connect.sink.SinkConnector;
import org.apache.kafka.common.config.ConfigDef;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class CustomSinkConnector extends SinkConnector {

    private String apiUrl;
    private String kafkaTopics;
    private long pollIntervalMs;

    @Override
    public String version() {
        return "1.0";
    }

    @Override
    public void start(Map<String, String> props) {
        this.apiUrl = props.get("api.url");
        this.kafkaTopics = props.get("topics");
        this.pollIntervalMs = Long.parseLong(props.getOrDefault("poll.interval.ms", "1000"));
    }

    @Override
    public Class<? extends Task> taskClass() {
        return CustomSinkTask.class;
    }

    @Override
    public List<Map<String, String>> taskConfigs(int maxTasks) {
        List<Map<String, String>> configs = new ArrayList<>();
        for (int i = 0; i < maxTasks; i++) {
            configs.add(Map.of(
                "api.url", apiUrl,
                "topics", kafkaTopics,
                "poll.interval.ms", String.valueOf(pollIntervalMs)
            ));
        }
        return configs;
    }

    @Override
    public void stop() {

    }

    @Override
    public ConfigDef config() {
        return new ConfigDef()
                .define("api.url", ConfigDef.Type.STRING, ConfigDef.Importance.HIGH, "REST API endpoint URL")
                .define("topics", ConfigDef.Type.STRING, ConfigDef.Importance.HIGH, "Kafka topics to consume data from")
                .define("poll.interval.ms", ConfigDef.Type.LONG, 1000, ConfigDef.Importance.MEDIUM, "Poll interval in milliseconds");
    }
}
