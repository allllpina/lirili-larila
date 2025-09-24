-- Initialization SQL for PostgreSQL schema
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

-- Таблиця користувачів
CREATE TABLE IF NOT EXISTS public.users (
    id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username        VARCHAR(255) NULL,
    email           VARCHAR(255) NOT NULL UNIQUE,
    password_hash   VARCHAR(255) NULL,
    is_oauth_user   BOOLEAN DEFAULT FALSE,
    oauth_provider  VARCHAR(50) NULL,
    oauth_sub       VARCHAR(255) NULL,
    refresh_token   TEXT NOT NULL,
    is_superuser    BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Додавання адміністратора (username=admin, пароль=admin)
INSERT INTO public.users (
    username, email, password_hash, is_oauth_user,
    refresh_token, is_superuser
) VALUES (
    'admin',
    'admin@example.com',
    '$2b$12$SI4UNbnWDiPGMEVLeozDs.E/k5lbEFL6PInSvJhxm.22M.NBi2.AW',
    FALSE,
    'initial_refresh_token',
    TRUE
)
ON CONFLICT (email) DO NOTHING;