package com.acme.kafka.connect.speed;

import org.junit.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static com.acme.kafka.connect.speed.SpeedSourceConnectorConfig.*;

public class SpeedSourceTaskTest {

    @Test
    public void taskVersionShouldMatch() {
        String version = PropertiesUtil.getConnectorVersion();
        assertEquals(version, new SpeedSourceTask().version());
    }

    @Test
    public void checkNumberOfRecords() {
        String[] sampleList = {"test1", "test2"};
        Map<String, String> connectorProps = new HashMap<>();
        connectorProps.put(DOES_THIS_WORK_CONFIG, "yes");
        connectorProps.put(PUBNUB_SUBSCRIBE_KEY_CONFIG, "Connect");
        connectorProps.put(PUBNUB_SUBSCRIBE_KEY_CONFIG, "Key");
        connectorProps.put(PUBNUB_CHANNELS_LIST, "List");
        connectorProps.put(NUMBER_OF_HOURS_CONFIG, "List");
        Map<String, String> taskProps = getTaskProps(connectorProps);
        SpeedSourceTask task = new SpeedSourceTask();
//        assertDoesNotThrow(() -> {
//            task.start(taskProps);
//            List<SourceRecord> records = task.poll();
//            assertEquals(1, records.size());
//        });
    }

    private Map<String, String> getTaskProps(Map<String, String> connectorProps) {
        SpeedSourceConnector connector = new SpeedSourceConnector();
        connector.start(connectorProps);
        List<Map<String, String>> taskConfigs = connector.taskConfigs(1);
        return taskConfigs.get(0);
    }
    
}
