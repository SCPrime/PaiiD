#!/bin/bash
# backup-database.sh - Automated database backups

TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_DIR="backups"
RETENTION_DAYS=7

echo "🗄️  Database Backup - $TIMESTAMP"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Get database URL from Render
if [ -z "$DATABASE_URL" ]; then
    echo "❌ DATABASE_URL not set"
    exit 1
fi

# Create backup
BACKUP_FILE="$BACKUP_DIR/paiid-backup-$TIMESTAMP.sql"
pg_dump "$DATABASE_URL" > "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    echo "✅ Backup created: $BACKUP_FILE"
    
    # Compress
    gzip "$BACKUP_FILE"
    echo "✅ Compressed: $BACKUP_FILE.gz"
    
    # Upload to S3 (optional)
    if command -v aws &> /dev/null && [ -n "$S3_BACKUP_BUCKET" ]; then
        aws s3 cp "$BACKUP_FILE.gz" "s3://$S3_BACKUP_BUCKET/backups/"
        echo "✅ Uploaded to S3"
    fi
    
    # Clean old backups
    find "$BACKUP_DIR" -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete
    echo "✅ Cleaned backups older than $RETENTION_DAYS days"
    
else
    echo "❌ Backup failed"
    exit 1
fi
