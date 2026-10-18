#!/bin/sh
set -e

python -m bot.init_database_postgres
exec python -m bot