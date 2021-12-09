CREATE TABLE public.prefecture(
    id SERIAL NOT NULL,
    prefecture_name VARCHAR NOT NULL UNIQUE,
    PRIMARY KEY(id)
);