package com.acme.kafka.connect.batch;

import com.google.gson.JsonNull;
import com.google.gson.JsonObject;
import org.apache.kafka.connect.data.Schema;
import org.apache.kafka.connect.data.SchemaBuilder;
import org.apache.kafka.connect.data.Struct;

public final class WeatherDataSchema {

    public static final String WIND_SPEED_FIELD = "wind_speed";
    public static final String CITY_FIELD = "city";
    public static final String WIND_CHILL_FIELD = "wind_chill";
    public static final String ELEVATION_FIELD = "elevation";
    public static final String TEMP_FIELD = "temp";
    public static final String UV_FIELD = "uv";
    public static final String LONGITUDE_FIELD = "longitude";
    public static final String HUMIDITY_FIELD = "humidity";
    public static final String WINDDIR_FIELD = "winddir";
    public static final String PRESSURE_FIELD = "pressure";
    public static final String LATITUDE_FIELD = "latitude";
    public static final String SOLAR_RADIATION_FIELD = "solar_radiation";
    public static final String PRECIP_RATE_FIELD = "precip_rate";
    public static final String TIMESTAMP_FIELD = "timestamp";

    private WeatherDataSchema() {
    }

    public static final Schema VALUE_SCHEMA = SchemaBuilder.struct().name("weatherData")
            .field(WIND_SPEED_FIELD, Schema.OPTIONAL_FLOAT64_SCHEMA)
            .field(CITY_FIELD, Schema.STRING_SCHEMA)
            .field(WIND_CHILL_FIELD, Schema.OPTIONAL_FLOAT64_SCHEMA)
            .field(ELEVATION_FIELD, Schema.OPTIONAL_FLOAT64_SCHEMA)
            .field(TEMP_FIELD, Schema.OPTIONAL_FLOAT64_SCHEMA)
            .field(UV_FIELD, Schema.OPTIONAL_FLOAT64_SCHEMA)
            .field(LONGITUDE_FIELD, Schema.OPTIONAL_FLOAT64_SCHEMA)
            .field(HUMIDITY_FIELD, Schema.OPTIONAL_FLOAT64_SCHEMA)
            .field(WINDDIR_FIELD, Schema.OPTIONAL_FLOAT64_SCHEMA)
            .field(PRESSURE_FIELD, Schema.OPTIONAL_FLOAT64_SCHEMA)
            .field(LATITUDE_FIELD, Schema.OPTIONAL_FLOAT64_SCHEMA)
            .field(SOLAR_RADIATION_FIELD, Schema.OPTIONAL_FLOAT64_SCHEMA)
            .field(PRECIP_RATE_FIELD, Schema.OPTIONAL_FLOAT64_SCHEMA)
            .field(TIMESTAMP_FIELD, Schema.INT64_SCHEMA)
            .build();

    public static Struct buildStruct(JsonObject json, Schema schema, Long timestamp) {
        Struct valueStruct = new Struct(schema)
                .put(WIND_SPEED_FIELD,
                        json.get("wind_speed") != JsonNull.INSTANCE ? json.get("wind_speed").getAsDouble() : null)
                .put(CITY_FIELD, json.get("city").getAsString())
                .put(WIND_CHILL_FIELD,
                        json.get("wind_chill") != JsonNull.INSTANCE ? json.get("wind_chill").getAsDouble() : null)
                .put(ELEVATION_FIELD,
                        json.get("elevation") != JsonNull.INSTANCE ? json.get("elevation").getAsDouble() : null)
                .put(TEMP_FIELD,
                        json.get("temp") != JsonNull.INSTANCE ? json.get("temp").getAsDouble() : null)
                .put(UV_FIELD,
                        json.get("uv") != JsonNull.INSTANCE ? json.get("uv").getAsDouble() : null)
                .put(LONGITUDE_FIELD,
                        json.get("longitude") != JsonNull.INSTANCE ? json.get("longitude").getAsDouble() : null)
                .put(HUMIDITY_FIELD,
                        json.get("humidity") != JsonNull.INSTANCE ? json.get("humidity").getAsDouble() : null)
                .put(WINDDIR_FIELD,
                        json.get("winddir") != JsonNull.INSTANCE ? json.get("winddir").getAsDouble() : null)
                .put(PRESSURE_FIELD,
                        json.get("pressure") != JsonNull.INSTANCE ? json.get("pressure").getAsDouble() : null)
                .put(LATITUDE_FIELD,
                        json.get("latitude") != JsonNull.INSTANCE ? json.get("latitude").getAsDouble() : null)
                .put(SOLAR_RADIATION_FIELD,
                        json.get("solar_radiation") != JsonNull.INSTANCE ? json.get("solar_radiation").getAsDouble() : null)
                .put(PRECIP_RATE_FIELD,
                        json.get("precip_rate") != JsonNull.INSTANCE ? json.get("precip_rate").getAsDouble() : null)
                .put(TIMESTAMP_FIELD, timestamp);
        return valueStruct;
    }

}
