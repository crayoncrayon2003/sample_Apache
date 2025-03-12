package com.example;

import org.apache.kafka.connect.source.SourceRecord;
import org.apache.kafka.connect.source.SourceTask;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class CustomSourceTask extends SourceTask {

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
    public List<SourceRecord> poll() throws InterruptedException {
        Thread.sleep(pollIntervalMs);

        List<SourceRecord> records = new ArrayList<>();
        try {
            HttpClient client = HttpClient.newHttpClient();
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(apiUrl))
                    .GET()
                    .build();

            HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
            
            // レスポンスが有効であることを確認
            if (response.statusCode() == 200 && response.body() != null && !response.body().isEmpty()) {
                SourceRecord sourceRecord = new SourceRecord(
                    null, // パーティション情報
                    null, // オフセット情報
                    kafkaTopics, // トピック名
                    null, // キースキーマ（オプション）
                    null, // キー（オプション）
                    null, // バリュースキーマ（オプション）
                    response.body() // HTTPレスポンスボディ
                );
                records.add(sourceRecord);
            } else {
                System.err.println("Invalid response: " + response.statusCode() + " " + response.body());
            }

        } catch (Exception e) {
            e.printStackTrace();
        }

        return records;
    }

    @Override
    public void stop() {

    }
}
