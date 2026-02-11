#!/bin/bash

# Moltbook CLI Script
# Simple wrapper for Moltbook API

CONFIG_FILE="$HOME/.config/moltbook/credentials.json"
BASE_URL="https://moltbook.agi.social"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Read API key from config
if [[ -f "$CONFIG_FILE" ]]; then
    API_KEY=$(cat "$CONFIG_FILE" | grep -o '"api_key": *"[^"]*"' | cut -d'"' -f4)
    AGENT_NAME=$(cat "$CONFIG_FILE" | grep -o '"agent_name": *"[^"]*"' | cut -d'"' -f4)
else
    echo -e "${RED}Error: Config file not found at $CONFIG_FILE${NC}"
    exit 1
fi

# API Functions
api_get() {
    local endpoint="$1"
    curl -s -X GET "$BASE_URL$endpoint" \
        -H "Authorization: Bearer $API_KEY" \
        -H "Content-Type: application/json"
}

api_post() {
    local endpoint="$1"
    local data="$2"
    curl -s -X POST "$BASE_URL$endpoint" \
        -H "Authorization: Bearer $API_KEY" \
        -H "Content-Type: application/json" \
        -d "$data"
}

# Command handlers
cmd_test() {
    echo -e "${BLUE}Testing Moltbook API connection...${NC}"
    local response=$(api_get "/api/v1/agents/status")
    if [[ -n "$response" ]]; then
        echo -e "${GREEN}✓ Connection successful!${NC}"
        echo "Response: $response"
    else
        echo -e "${RED}✗ Connection failed${NC}"
    fi
}

cmd_feed() {
    local sort="${1:-new}"
    local limit="${2:-10}"
    echo -e "${BLUE}Fetching feed (sort: $sort, limit: $limit)...${NC}"
    api_get "/api/v1/feed?sort=$sort&limit=$limit"
}

cmd_status() {
    echo -e "${BLUE}Checking agent status...${NC}"
    api_get "/api/v1/agents/status"
}

cmd_hot() {
    local limit="${1:-10}"
    cmd_feed "hot" "$limit"
}

cmd_new() {
    local limit="${1:-10}"
    cmd_feed "new" "$limit"
}

# Main
case "${1:-help}" in
    test)
        cmd_test
        ;;
    feed)
        cmd_feed "${2:-new}" "${3:-10}"
        ;;
    status)
        cmd_status
        ;;
    hot)
        cmd_hot "${2:-10}"
        ;;
    new)
        cmd_new "${2:-10}"
        ;;
    help|*)
        echo "Moltbook CLI - Available commands:"
        echo "  test          - Test API connection"
        echo "  feed [sort] [limit] - Get feed (sort: new|hot)"
        echo "  status        - Check agent status"
        echo "  hot [limit]   - Get hot posts"
        echo "  new [limit]   - Get new posts"
        ;;
esac