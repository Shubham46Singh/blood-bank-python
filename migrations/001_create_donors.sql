CREATE TABLE IF NOT EXISTS donors (
    id            SERIAL PRIMARY KEY,
    name          TEXT NOT NULL,
    blood_group   TEXT NOT NULL CHECK (blood_group IN
                   ('O-','O+','A-','A+','B-','B+','AB-','AB+')),
    distance_km   NUMERIC(6,1) NOT NULL DEFAULT 0,
    age           INT,
    last_donation DATE,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS requests (
    id          SERIAL PRIMARY KEY,
    hospital    TEXT NOT NULL,
    blood_group TEXT NOT NULL,
    units       INT  NOT NULL CHECK (units > 0),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS donors_group ON donors (blood_group);
