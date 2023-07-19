DROP TABLE IF EXISTS somtodayqueue;

CREATE TABLE somtodayqueue(
    discordID BIGINT,
    linked BOOLEAN
);

DROP TABLE IF EXISTS somtodaytokens;

CREATE TABLE IF NOT EXISTS somtodaytokens(
    ssotoken TEXT,
    discordID BIGINT

);

