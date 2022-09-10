-- Schema for ticker gathering

CREATE TABLE IF NOT EXISTS usernames (
        id           INTEGER PRIMARY KEY NOT NULL,
        username     VARCHAR(50) NOT NULL,
        joined       VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS tickers (
	    id           INTEGER NOT NULL,
	    username     VARCHAR(50) NOT NULL,
	    ticker       VARCHAR(50) NOT NULL,
	    name         VARCHAR(50) NOT NULL,
	    price        FLOAT NOT NULL,
	    created      VARCHAR(50) NOT NULL,
	    updated	     VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS news (
	ticker		VARCHAR(10) PRIMARY KEY NOT NULL,
	header		VARCHAR(100) NOT NULL,
	time		VARCHAR(50) NOT NULL,
	updated		VARCHAR(50) NOT NULL
);
