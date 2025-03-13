FROM confluentinc/cp-kafka-connect:7.9.0

USER root

# プラグインディレクトリを作成
RUN mkdir -p /usr/share/confluent-hub-components/custom-connectors
# カスタムコネクタ（SourceとSink）のJARファイルをコピー
COPY ./kafka-custom-connector /usr/share/confluent-hub-components/custom-connectors/

# プラグインディレクトリの所有権を更新
RUN chown -R appuser:appuser /usr/share/confluent-hub-components

USER appuser

# Kafka Connect RESTポートを公開
EXPOSE 8083
