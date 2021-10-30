-- Schema for ticker gathering

create table usernames (
        id           integer primary key,
        username     text,
        joined       text
);

create table tickers (
	    id           integer,
	    username     text,
	    ticker       text,
	    name         text,
	    price        text,
	    created      text,
	    updated	 text
);

create table news (
	ticker		text primary key,
	header		text,
	time		text,
	updated		text
);
