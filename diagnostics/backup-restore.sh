#!/bin/bash
# BACKUP AND RESTORE UTILITY - Backup your OpenClaw configuration and data

set -e

BACKUP_DIR="$HOME/.openclaw-backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="openclaw-backup-$DATE"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_header() {
    clear
    cat << 'EOF'
╔════════════════════════════════════════════════════════════════╗
║         OpenClaw Backup & Restore Utility                      ║
╚════════════════════════════════════════════════════════════════╝
EOF
}

print_header

case "$1" in
    backup)
        echo -e "${GREEN}Creating backup...${NC}"
        echo ""

        mkdir -p "$BACKUP_DIR"

        # Create backup
        echo "Backing up configuration..."
        tar -czf "$BACKUP_DIR/$BACKUP_NAME.tar.gz" \
            -C "$HOME" \
            .openclaw 2>/dev/null || true

        if [ -f "$BACKUP_DIR/$BACKUP_NAME.tar.gz" ]; then
            SIZE=$(du -h "$BACKUP_DIR/$BACKUP_NAME.tar.gz" | cut -f1)
            echo -e "${GREEN}✓ Backup created successfully!${NC}"
            echo ""
            echo "Backup location: $BACKUP_DIR/$BACKUP_NAME.tar.gz"
            echo "Backup size: $SIZE"
            echo ""
            echo "To restore this backup later:"
            echo "  $0 restore $BACKUP_NAME"
        else
            echo -e "${RED}✗ Backup failed!${NC}"
            exit 1
        fi
        ;;

    restore)
        if [ -z "$2" ]; then
            echo -e "${RED}Error: Please specify backup name${NC}"
            echo ""
            echo "Available backups:"
            ls -1 "$BACKUP_DIR"/*.tar.gz 2>/dev/null | xargs -n1 basename 2>/dev/null || echo "  No backups found"
            exit 1
        fi

        BACKUP_PATH="$BACKUP_DIR/$2.tar.gz"

        if [ ! -f "$BACKUP_PATH" ]; then
            echo -e "${RED}Error: Backup not found: $BACKUP_PATH${NC}"
            exit 1
        fi

        echo -e "${YELLOW}WARNING: This will overwrite your current OpenClaw configuration!${NC}"
        echo ""
        read -p "Are you sure you want to restore from '$2'? (yes/no): " confirm

        if [ "$confirm" != "yes" ]; then
            echo "Restore cancelled."
            exit 0
        fi

        echo ""
        echo -e "${GREEN}Restoring backup...${NC}"
        echo ""

        # Stop gateway first
        if systemctl is-active --quiet openclaw-gateway; then
            echo "Stopping OpenClaw gateway..."
            sudo systemctl stop openclaw-gateway || true
        fi

        # Restore backup
        echo "Restoring files..."
        tar -xzf "$BACKUP_PATH" -C "$HOME"

        # Restart gateway
        echo "Starting OpenClaw gateway..."
        sudo systemctl start openclaw-gateway || true

        echo ""
        echo -e "${GREEN}✓ Backup restored successfully!${NC}"
        echo ""
        echo "Your OpenClaw configuration has been restored from '$2'."
        ;;

    list)
        echo -e "${GREEN}Available backups:${NC}"
        echo ""

        if [ -d "$BACKUP_DIR" ] && [ "$(ls -A $BACKUP_DIR/*.tar.gz 2>/dev/null)" ]; then
            ls -lh "$BACKUP_DIR"/*.tar.gz 2>/dev/null | awk '{
                printf "  %s  %s  %s\n", $9, $5, $6 " " $7 " " $8
            }' | sed 's|.*/||'
        else
            echo "  No backups found"
        fi
        ;;

    clean)
        echo -e "${YELLOW}This will delete all backups!${NC}"
        echo ""
        read -p "Are you sure? (yes/no): " confirm

        if [ "$confirm" = "yes" ]; then
            rm -rf "$BACKUP_DIR"
            echo -e "${GREEN}✓ All backups deleted${NC}"
        else
            echo "Clean cancelled."
        fi
        ;;

    *)
        echo "OpenClaw Backup & Restore Utility"
        echo ""
        echo "Usage: $0 {backup|restore|list|clean} [backup_name]"
        echo ""
        echo "Commands:"
        echo "  backup           Create a new backup"
        echo "  restore <name>   Restore from a specific backup"
        echo "  list             List all available backups"
        echo "  clean            Delete all backups"
        echo ""
        echo "Examples:"
        echo "  $0 backup"
        echo "  $0 restore openclaw-backup-20260521_100000"
        echo "  $0 list"
        echo ""
esac