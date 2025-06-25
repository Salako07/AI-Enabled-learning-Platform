#!/bin/bash

echo "Setting up PostgreSQL database..."

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "Installing PostgreSQL..."
    
    # Ubuntu/Debian
    if command -v apt-get &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y postgresql postgresql-contrib
    # macOS with Homebrew
    elif command -v brew &> /dev/null; then
        brew install postgresql
        brew services start postgresql
    # CentOS/RHEL
    elif command -v yum &> /dev/null; then
        sudo yum install -y postgresql postgresql-server
        sudo postgresql-setup initdb
        sudo systemctl start postgresql
        sudo systemctl enable postgresql
    else
        echo "Please install PostgreSQL manually"
        exit 1
    fi
fi

# Create database and user
sudo -u postgres psql << EOSQL
CREATE DATABASE codemaster_db;
CREATE USER codemaster WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE codemaster_db TO codemaster;
ALTER USER codemaster CREATEDB;
\q
EOSQL

echo "✅ Database setup complete"
