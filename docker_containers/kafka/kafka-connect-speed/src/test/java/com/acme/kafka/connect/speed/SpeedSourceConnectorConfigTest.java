package com.acme.kafka.connect.speed;

import java.util.HashMap;
import java.util.Map;

import org.apache.kafka.common.config.ConfigException;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static com.acme.kafka.connect.speed.SpeedSourceConnectorConfig.*;

public class SpeedSourceConnectorConfigTest {

    @Test
    public void basicParamsAreMandatory() {
        assertThrows(ConfigException.class, () -> {
            Map<String, String> props = new HashMap<>();
            new SpeedSourceConnectorConfig(props);
        });
    }

    public void checkingNonRequiredDefaults() {
        Map<String, String> props = new HashMap<>();
        SpeedSourceConnectorConfig config = new SpeedSourceConnectorConfig(props);
        assertEquals("foo", config.getString(FIRST_NONREQUIRED_PARAM_CONFIG));
        assertEquals("bar", config.getString(SECOND_NONREQUIRED_PARAM_CONFIG));
    }

}
