CREATE TABLE public.area(
	id INTEGER NOT NULL UNIQUE,
	area_name VARCHAR NOT NULL UNIQUE,
	prefecture_id INTEGER NOT NULL,
	FOREIGN KEY (prefecture_id) REFERENCES public.prefecture(id) ON DETELE CASCADE ON UPDATE CASCADE,
	PRIMARY KEY (id)
);