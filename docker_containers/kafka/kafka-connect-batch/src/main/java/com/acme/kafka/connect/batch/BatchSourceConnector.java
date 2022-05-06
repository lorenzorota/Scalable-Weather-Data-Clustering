package com.acme.kafka.connect.batch;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import org.apache.kafka.common.config.Config;
import org.apache.kafka.common.config.ConfigDef;
import org.apache.kafka.common.config.ConfigValue;
import org.apache.kafka.connect.connector.Task;
import org.apache.kafka.connect.errors.ConnectException;
import org.apache.kafka.connect.source.SourceConnector;
import org.apache.kafka.connect.util.ConnectorUtils;

import static com.acme.kafka.connect.batch.BatchSourceConnectorConfig.*;

public class BatchSourceConnector extends SourceConnector {

    private final Logger log = LoggerFactory.getLogger(BatchSourceConnector.class);

    private Map<String, String> originalProps;
    private BatchSourceConnectorConfig config;
    private SourceMonitorThread sourceMonitorThread;

    @Override
    public String version() {
        return PropertiesUtil.getConnectorVersion();
    }

    @Override
    public ConfigDef config() {
        return CONFIG_DEF;
    }

    @Override
    public Class<? extends Task> taskClass() {
        return BatchSourceTask.class;
    }

    @Override
    public Config validate(Map<String, String> connectorConfigs) {
        Config config = super.validate(connectorConfigs);
        List<ConfigValue> configValues = config.configValues();
        boolean missingTopicDefinition = true;
        for (ConfigValue configValue : configValues) {
            if (configValue.name().equals(DOES_THIS_WORK_CONFIG)) {
                if (configValue.value() != null) {
                    missingTopicDefinition = false;
                    break;
                }
            }
        }
        if (missingTopicDefinition) {
            throw new ConnectException(String.format(
                "There is no definition of [XYZ] in the "
                + "configuration. Either the property "
                + "'%s' or '%s' must be set in the configuration.",
                FIRST_NONREQUIRED_PARAM_CONFIG,
                SECOND_NONREQUIRED_PARAM_CONFIG));
        }
        return config;
    }

    @Override
    public void start(Map<String, String> originalProps) {
        this.originalProps = originalProps;
        config = new BatchSourceConnectorConfig(originalProps);
        String firstParam = config.getString(FIRST_NONREQUIRED_PARAM_CONFIG);
        String secondParam = config.getString(SECOND_NONREQUIRED_PARAM_CONFIG);
        List<String> channelsList = config.getList(PUBNUB_CHANNELS_LIST);
        int monitorThreadTimeout = config.getInt(MONITOR_THREAD_TIMEOUT_CONFIG);
        sourceMonitorThread = new SourceMonitorThread(
            context, firstParam, secondParam, channelsList, monitorThreadTimeout);
        sourceMonitorThread.start();
    }

    @Override
    public List<Map<String, String>> taskConfigs(int maxTasks) {
        List<Map<String, String>> taskConfigs = new ArrayList<>();
        // The partitions below represent the source's part that
        // would likely to be broken down into tasks... such as
        // tables in a database.
//        List<String> partitions = sourceMonitorThread.getCurrentSources();
        List<String> partitions = sourceMonitorThread.getListOfChannels();
        if (partitions.isEmpty()) {
            taskConfigs = Collections.emptyList();
            log.warn("No tasks created because there is zero to work on");
        } else {
            int numTasks = Math.min(partitions.size(), maxTasks);
            List<List<String>> partitionSources = ConnectorUtils.groupPartitions(partitions, numTasks);
            for (List<String> source : partitionSources) {
                Map<String, String> taskConfig = new HashMap<>(originalProps);
                taskConfig.put("sources", String.join(",", source));
                taskConfigs.add(taskConfig);
            }
        }
        return taskConfigs;
    }

    @Override
    public void stop() {
        sourceMonitorThread.shutdown();
    }

}
