-- Initialize PostgreSQL databases for development and production
-- Development database
CREATE DATABASE task_db_dev;

-- Production database (main)
-- Already created as POSTGRES_DB in docker-compose

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE task_db_dev TO postgres;
GRANT ALL PRIVILEGES ON DATABASE task_db TO postgres;
