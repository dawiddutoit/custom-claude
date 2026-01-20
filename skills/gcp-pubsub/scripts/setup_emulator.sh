#!/bin/bash

# Setup Google Cloud Pub/Sub Emulator for local development
# This script installs the emulator and provides configuration options

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Google Cloud Pub/Sub Emulator Setup${NC}"
echo "======================================"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}Error: gcloud CLI is not installed${NC}"
    echo "Install from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

echo -e "${YELLOW}Step 1: Installing Pub/Sub Emulator${NC}"
gcloud components install pubsub-emulator

echo -e "${GREEN}✓ Emulator installed${NC}"

# Get optional parameters
EMULATOR_HOST="${PUBSUB_EMULATOR_HOST:-localhost:8085}"
PROJECT_ID="${GCLOUD_PROJECT:-test-project}"
PORT="${EMULATOR_PORT:-8085}"

echo ""
echo -e "${YELLOW}Step 2: Configuration${NC}"
echo "Emulator Host: $EMULATOR_HOST"
echo "Project ID: $PROJECT_ID"
echo "Port: $PORT"

# Create .env file for local development
echo ""
echo -e "${YELLOW}Step 3: Creating .env file for local development${NC}"

cat > .env.local <<EOF
# Google Cloud Pub/Sub Emulator Configuration
PUBSUB_EMULATOR_HOST=localhost:$PORT
GOOGLE_CLOUD_PROJECT=$PROJECT_ID
GCLOUD_PROJECT=$PROJECT_ID
EOF

echo -e "${GREEN}✓ Created .env.local${NC}"
echo "Use: source .env.local"

echo ""
echo -e "${YELLOW}Step 4: How to run the emulator${NC}"
echo ""
echo "Option A - In a separate terminal:"
echo "  gcloud beta emulators pubsub start --host-port=localhost:$PORT"
echo ""
echo "Option B - Using this script with background process:"
echo "  ./$(basename $0) --start"
echo ""

# Optional: Start emulator in background
if [[ "$1" == "--start" ]]; then
    echo -e "${YELLOW}Starting Pub/Sub Emulator...${NC}"
    export PUBSUB_EMULATOR_HOST="localhost:$PORT"
    gcloud beta emulators pubsub start --host-port="localhost:$PORT" &
    EMULATOR_PID=$!
    echo -e "${GREEN}✓ Emulator started (PID: $EMULATOR_PID)${NC}"
    echo "Store this PID if you want to stop it later: kill $EMULATOR_PID"

    # Wait for emulator to be ready
    echo "Waiting for emulator to be ready..."
    for i in {1..30}; do
        if nc -z localhost $PORT 2>/dev/null; then
            echo -e "${GREEN}✓ Emulator is ready!${NC}"
            break
        fi
        echo -n "."
        sleep 1
    done
fi

echo ""
echo -e "${GREEN}Setup Complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Source the environment: source .env.local"
echo "2. Start the emulator in another terminal: gcloud beta emulators pubsub start"
echo "3. Run your application"
echo ""
echo "To verify the setup, run:"
echo "  python pubsub_utils.py --list-topics"
