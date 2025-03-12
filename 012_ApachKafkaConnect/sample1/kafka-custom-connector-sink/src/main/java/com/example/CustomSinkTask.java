package com.example;

import org.apache.kafka.connect.sink.SinkRecord;
import org.apache.kafka.connect.sink.SinkTask;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.util.Collection;
import java.util.Map;

public class CustomSinkTask extends SinkTask {

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
    public void put(Collection<SinkRecord> records) {
        HttpClient client = HttpClient.newHttpClient();

        for (SinkRecord record : records) {
            try {
                String topic = record.topic();

                if (!topic.equals(kafkaTopics)) {
                    System.err.println("Skipping record from unmatched topic: " + topic);
                    return;
                }

                String recordValue = record.value().toString();

                HttpRequest request = HttpRequest.newBuilder()
                        .uri(URI.create(apiUrl))
                        .header("Content-Type", "application/json")
                        .POST(HttpRequest.BodyPublishers.ofString(recordValue, StandardCharsets.UTF_8))
                        .build();

                HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
                System.out.println("Response: " + response.statusCode() + " " + response.body());

                Thread.sleep(pollIntervalMs);

            } catch (Exception e) {
                e.printStackTrace();
            }
        }
    }

    @Override
    public void stop() {
    }
}
