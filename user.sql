CREATE TABLE users (
    user_id BIGSERIAL NOT NULL PRIMARY KEY,
    full_name VARCHAR(50) NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(150),
    points INTEGER DEFAULT 0,
    password VARCHAR(255) NOT NULL
);