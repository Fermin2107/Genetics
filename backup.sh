#!/bin/bash
PGUSER="postgres"
PGPASSWORD="Gurruchaga46"
DBNAME="animalesdb"
BACKUP_DIR=""C:\Users\fermi\OneDrive\Documents\Backups""
DATE=$(date +"%Y%m%d_%H%M")

export PGPASSWORD
mkdir -p "$BACKUP_DIR"
pg_dump -U $PGUSER -h localhost $DBNAME > "$BACKUP_DIR/animalesdb_$DATE.sql"
unset PGPASSWORD
