#!/bin/bash
# Automated Database Backup Script
# Safely backs up database without disrupting service

set -e

# Configuration
BACKUP_DIR="/home/tele/manufatures/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_FILE="/home/tele/manufatures/db.sqlite3"
BACKUP_FILE="$BACKUP_DIR/db_backup_$DATE.sqlite3"
MAX_BACKUPS=30  # Keep last 30 backups

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

echo "📦 Starting database backup..."

# Check if database exists
if [ ! -f "$DB_FILE" ]; then
    echo "❌ Database file not found: $DB_FILE"
    exit 1
fi

# Create backup
cp "$DB_FILE" "$BACKUP_FILE"

# Compress backup to save space
gzip "$BACKUP_FILE"
BACKUP_FILE="${BACKUP_FILE}.gz"

# Verify backup was created
if [ -f "$BACKUP_FILE" ]; then
    SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo "✅ Backup created: $(basename $BACKUP_FILE) ($SIZE)"
else
    echo "❌ Backup failed!"
    exit 1
fi

# Clean up old backups (keep last MAX_BACKUPS)
echo "🧹 Cleaning old backups (keeping last $MAX_BACKUPS)..."
cd "$BACKUP_DIR"
ls -t db_backup_*.sqlite3.gz 2>/dev/null | tail -n +$((MAX_BACKUPS + 1)) | xargs -r rm
echo "   $(ls -1 db_backup_*.sqlite3.gz 2>/dev/null | wc -l) backups remaining"

echo ""
echo "✅ Backup complete!"
echo "   Location: $BACKUP_FILE"
echo ""
echo "To restore: gunzip -c $BACKUP_FILE > /home/tele/manufatures/db.sqlite3"
