CREATE DATABASE diagnostico;
CREATE USER diagnostico;
GRANT ALL ON DATABASE diagnostico TO "diagnostico";
ALTER USER diagnostico PASSWORD 'development';
ALTER USER diagnostico CREATEDB;