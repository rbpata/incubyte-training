-- Microservices database init
-- auth_service_db is already created as POSTGRES_DB in docker-compose
-- Create the task_service_db alongside it
CREATE DATABASE task_service_db;

GRANT ALL PRIVILEGES ON DATABASE auth_service_db TO postgres;

GRANT ALL PRIVILEGES ON DATABASE task_service_db TO postgres;