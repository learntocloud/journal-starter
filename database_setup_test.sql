-- Provision the disposable test database without modifying the application database.
SELECT 'CREATE DATABASE career_journal_test'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'career_journal_test')
\gexec

\connect career_journal_test
\ir database_setup.sql
