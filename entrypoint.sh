#!/bin/sh
set -e

python -m recreate_database_postgres
exec python -m bot