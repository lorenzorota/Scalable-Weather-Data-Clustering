package com.acme.kafka.connect.batch;

import java.util.*;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;

import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.pubnub.api.PNConfiguration;
import com.pubnub.api.PubNub;
import com.pubnub.api.PubNubException;
import com.pubnub.api.models.consumer.history.PNFetchMessageItem;
import com.pubnub.api.models.consumer.history.PNFetchMessagesResult;
import org.apache.kafka.connect.data.Struct;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.apache.kafka.connect.source.SourceRecord;
import org.apache.kafka.connect.source.SourceTask;

import static com.acme.kafka.connect.batch.BatchSourceConnectorConfig.*;
import static com.acme.kafka.connect.batch.WeatherDataSchema.*;

public class BatchSourceTask extends SourceTask {

    private static Logger log = LoggerFactory.getLogger(BatchSourceTask.class);

    private BatchSourceConnectorConfig config;
    private String name;
    private int monitorThreadTimeout;
    private List<String> sources;
    private PubNub pubNub;
    private PNConfiguration pnConfiguration;

    private Integer numHours;
    private Long startTimetoken;
    private Long endTimetoken;
    private HashMap<String, Long> offset;
    private HashMap<String, Boolean> sourceFetchedStatus;

    // defining our 'magic' numbers
    private final int numDays = 7;
    private final Long tenThousand = 10000L;
    private final int maxItems = 100;
    private final int errorCodeIO = 5;

    @Override
    public String version() {
        return PropertiesUtil.getConnectorVersion();
    }

    @Override
    public void start(Map<String, String> properties) {
        config = new BatchSourceConnectorConfig(properties);
        offset = new HashMap<String, Long>();
        sourceFetchedStatus = new HashMap<String, Boolean>();
        numHours = Integer.parseInt(config.getString(NUMBER_OF_HOURS_CONFIG));
        monitorThreadTimeout = config.getInt(MONITOR_THREAD_TIMEOUT_CONFIG);
        String subscribeKey = config.getString(PUBNUB_SUBSCRIBE_KEY_CONFIG);
        String sourcesStr = properties.get("sources");
        name = properties.get("name");
        sources = Arrays.asList(sourcesStr.split(","));

        // declare the start and end timetoken based on the numbers of hours in the config
        Long timestampNow = Calendar.getInstance().getTimeInMillis();
        startTimetoken = (timestampNow - TimeUnit.HOURS.toMillis(numHours)) * tenThousand;
        endTimetoken = timestampNow * tenThousand;

        log.info("Retrieving data from " + startTimetoken + " until " + endTimetoken);

        // set initial offsets to start timetoken
        for (String source : sources) {
            offset.put(source, startTimetoken);
        }

        // set states to track if source fetching is complete
        for (String source : sources) {
            sourceFetchedStatus.put(source, false);
        }

        // now we initialize the PubNub connection
        try {
            pnConfiguration = new PNConfiguration("kafka-historic-data-connector");
        } catch (PubNubException e) {
            e.printStackTrace();
        }

        pnConfiguration.setSubscribeKey(subscribeKey);
        pubNub = new PubNub(pnConfiguration);

    }

    @Override
    public List<SourceRecord> poll() throws InterruptedException {
        List<SourceRecord> records = new ArrayList<>();

        final CountDownLatch latch = new CountDownLatch(1);

        for (String source : sources) {
            Long updatedStartTimetoken = offset.get(source);
            log.info("- fetching from offset: " + updatedStartTimetoken + " for source " + source);
            String topic = "common";

            // fetch first page and store in records
            final Long timeToken;
            timeToken = updatedStartTimetoken;
            PNFetchMessagesResult result;

            if (!sourceFetchedStatus.get(source)) {
                try {
                    String channel = source.replace("_", "%20");
                    result = pubNub.fetchMessages()
                            .channels(Arrays.asList(channel)) // where to fetch history from
                            .start(updatedStartTimetoken) // first timestamp
                            .end(endTimetoken) // last timestamp
                            .maximumPerChannel(maxItems)
                            .sync();

                    // if no exception raised then successful
                    if (result.getChannels().size() != 0) {
                        Long itemTimetoken = timeToken;

                        for (List<PNFetchMessageItem> items : result.getChannels().values()) {
                            for (PNFetchMessageItem item : items) {
                                if (item.getTimetoken() < endTimetoken) {
                                    JsonElement msg = item.getMessage();
                                    itemTimetoken = item.getTimetoken();
                                    Long timestamp =  itemTimetoken / tenThousand;
                                    JsonObject jsonMsg = msg.getAsJsonObject();
                                    Struct values = buildStruct(jsonMsg, VALUE_SCHEMA, timestamp);

                                    records.add(new SourceRecord(
                                            Collections.singletonMap("source", topic),
                                            Collections.singletonMap("offset", updatedStartTimetoken),
                                            topic, null, null, null, VALUE_SCHEMA,
                                            values));
                                }
                            }
                        }
                        offset.put(source, itemTimetoken);
                    } else {
                        // we should now have finished paging the records
                        log.info("Retrieved all historic data for: " + source);
                        sourceFetchedStatus.put(source, true);
                        throw new InterruptedException("Killed thread that was processing: " + source);

                    }
                } catch (PubNubException e) {
                    // if exception occurs, we consider the task to be finished
                    e.printStackTrace();
                    sourceFetchedStatus.put(source, true);
                    throw new InterruptedException("Killed thread that was processing: " + source);
                }
            }
        }

        return records;
    }

    @Override
    public void stop() {
    }
}
