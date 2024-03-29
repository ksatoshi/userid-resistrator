CREATE TABLE public.verify(
    id UUID NOT NULL UNIQUE,
    pass VARCHAR NOT NULL,
    user_id INTEGER NOT NULL UNIQUE,
    FOREIGN KEY (user_id) REFERENCES public.user(id) ON DELETE CASCADE ON UPDATE CASCADE,
    PRIMARY KEY (id)
);