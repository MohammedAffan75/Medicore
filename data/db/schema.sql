-- data/db/schema.sql

-- Drop the schema if it exists to allow for clean re-runs
DROP SCHEMA IF EXISTS healthcare CASCADE;

-- Create the schema
CREATE SCHEMA healthcare;

-- Set the default search path to the new schema
SET search_path TO healthcare, public;

-- Enable UUID extension if needed (commonly needed for modern apps, though we'll use serial for simplicity if not strictly requiring UUIDs. Let's use UUIDs for modern practice).
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
