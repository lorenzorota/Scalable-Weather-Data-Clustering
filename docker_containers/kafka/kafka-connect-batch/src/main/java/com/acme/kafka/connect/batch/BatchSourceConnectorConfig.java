package com.acme.kafka.connect.batch;

import java.util.Map;

import org.apache.kafka.common.config.AbstractConfig;
import org.apache.kafka.common.config.ConfigDef;
import org.apache.kafka.common.config.ConfigDef.Importance;
import org.apache.kafka.common.config.ConfigDef.Type;

public class BatchSourceConnectorConfig extends AbstractConfig {

    public BatchSourceConnectorConfig(final Map<?, ?> originalProps) {
        super(CONFIG_DEF, originalProps);
    }

    public static final String DOES_THIS_WORK_CONFIG = "does.this.work";
    private static final String DOES_THIS_WORK_DOC = "This is for validation";

    public static final String FIRST_NONREQUIRED_PARAM_CONFIG = "first.nonrequired.param";
    private static final String FIRST_NONREQUIRED_PARAM_DOC = "This is the 1st non-required parameter";
    private static final String FIRST_NONREQUIRED_PARAM_DEFAULT = "foo";

    public static final String SECOND_NONREQUIRED_PARAM_CONFIG = "second.nonrequired.param";
    private static final String SECOND_NONREQUIRED_PARAM_DOC = "This is the 2ns non-required parameter";
    private static final String SECOND_NONREQUIRED_PARAM_DEFAULT = "bar";

    public static final String MONITOR_THREAD_TIMEOUT_CONFIG = "monitor.thread.timeout";
    private static final String MONITOR_THREAD_TIMEOUT_DOC = "Timeout used by the monitoring thread";
    private static final int MONITOR_THREAD_TIMEOUT_DEFAULT = 10000;

    // Here we define our config strings to be used by the PubNub API
    public static final String PUBNUB_SUBSCRIBE_KEY_CONFIG = "pubnub.subscribe.key";
    private static final String PUBNUB_SUBSCRIBE_KEY_DOC = "The subscribe key to be used by the PubNub API";

    public static final String PUBNUB_CHANNELS_LIST = "pubnub.channels";
    private static final String PUBNUB_CHANNELS_DOC = "List of strings that represent separate PubNub channels";

    public static final String NUMBER_OF_HOURS_CONFIG = "pubnub.historic.hours";
    private static final String NUMBER_OF_HOURS_DOC = "The number of hours subtracted from current time in retrieval";

    public static final ConfigDef CONFIG_DEF = createConfigDef();

    private static ConfigDef createConfigDef() {
        ConfigDef configDef = new ConfigDef();
        addParams(configDef);
        return configDef;
    }

    private static void addParams(final ConfigDef configDef) {
        configDef.define(
            DOES_THIS_WORK_CONFIG,
            Type.STRING,
            Importance.HIGH,
            DOES_THIS_WORK_DOC)
        .define(
            FIRST_NONREQUIRED_PARAM_CONFIG,
            Type.STRING,
            FIRST_NONREQUIRED_PARAM_DEFAULT,
            Importance.HIGH,
            FIRST_NONREQUIRED_PARAM_DOC)
        .define(
            SECOND_NONREQUIRED_PARAM_CONFIG,
            Type.STRING,
            SECOND_NONREQUIRED_PARAM_DEFAULT,
            Importance.HIGH,
            SECOND_NONREQUIRED_PARAM_DOC)
        .define(
            MONITOR_THREAD_TIMEOUT_CONFIG,
            Type.INT,
            MONITOR_THREAD_TIMEOUT_DEFAULT,
            Importance.LOW,
            MONITOR_THREAD_TIMEOUT_DOC)
        .define(
            PUBNUB_SUBSCRIBE_KEY_CONFIG,
            Type.STRING,
            Importance.HIGH,
            PUBNUB_SUBSCRIBE_KEY_DOC)
        .define(
            PUBNUB_CHANNELS_LIST,
            Type.LIST,
            Importance.HIGH,
            PUBNUB_CHANNELS_DOC)
        .define(
            NUMBER_OF_HOURS_CONFIG,
            Type.STRING,
            Importance.HIGH,
            NUMBER_OF_HOURS_DOC);
    }

}
