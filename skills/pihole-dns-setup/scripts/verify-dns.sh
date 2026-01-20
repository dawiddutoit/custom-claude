#!/bin/bash
#
# DNS Verification Script
# =======================
# Verifies Pi-hole DNS resolution for all configured domains.
#
# Usage:
#   ./scripts/verify-dns.sh           # Test all domains
#   ./scripts/verify-dns.sh pihole    # Test single domain
#   ./scripts/verify-dns.sh -v        # Verbose output
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Determine script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
PROJECT_DIR="$(dirname "$PROJECT_DIR")"  # Go up one more level from .claude/skills/pihole-dns-setup/scripts
CONFIG_FILE="$PROJECT_DIR/domains.toml"

# Default Pi-hole IP (auto-detect or fallback)
PI_IP="${PI_IP:-$(hostname -I 2>/dev/null | awk '{print $1}' || echo '192.168.68.135')}"

# Verbose mode
VERBOSE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS] [SUBDOMAIN]"
            echo ""
            echo "Options:"
            echo "  -v, --verbose    Show detailed output"
            echo "  -h, --help       Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0               Test all configured domains"
            echo "  $0 pihole        Test only pihole.temet.ai"
            echo "  $0 -v            Verbose output for all domains"
            exit 0
            ;;
        *)
            SINGLE_DOMAIN="$1"
            shift
            ;;
    esac
done

# Check if dig is available
if ! command -v dig &> /dev/null; then
    echo -e "${RED}Error: 'dig' command not found. Install dnsutils:${NC}"
    echo "  sudo apt-get install dnsutils"
    exit 1
fi

# Check if config file exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo -e "${RED}Error: Configuration file not found: $CONFIG_FILE${NC}"
    exit 1
fi

# Parse domains from config file using Python
get_domains() {
    python3 - "$CONFIG_FILE" << 'EOF'
import tomli
import sys

with open(sys.argv[1], "rb") as f:
    config = tomli.load(f)

domain = config.get("global", {}).get("domain", "temet.ai")
services = config.get("services", [])

for service in services:
    subdomain = service.get("subdomain", "")
    dns_ip = service.get("dns_ip", "")

    if not dns_ip:
        continue

    full_domain = f"{subdomain}.{domain}" if subdomain else domain
    print(f"{full_domain}:{dns_ip}")
EOF
}

# Test DNS resolution
test_dns() {
    local full_domain="$1"
    local expected_ip="$2"

    local result=$(dig @"$PI_IP" "$full_domain" +short 2>/dev/null | head -1)

    if [ -z "$result" ]; then
        echo -e "${RED}[FAIL]${NC} $full_domain -> ${RED}NXDOMAIN (no response)${NC}"
        return 1
    elif [ "$result" = "$expected_ip" ]; then
        echo -e "${GREEN}[PASS]${NC} $full_domain -> $result"
        return 0
    else
        echo -e "${YELLOW}[WARN]${NC} $full_domain -> Expected: $expected_ip, Got: $result"
        return 1
    fi
}

# Main execution
echo -e "${BLUE}DNS Verification Report${NC}"
echo "========================"
echo ""
echo -e "Pi-hole IP: ${BLUE}$PI_IP${NC}"
echo -e "Config file: $CONFIG_FILE"
echo ""

passed=0
failed=0

if [ -n "$SINGLE_DOMAIN" ]; then
    # Test single domain
    entry=$(get_domains | grep "^$SINGLE_DOMAIN\." || get_domains | grep "^$SINGLE_DOMAIN:")
    if [ -z "$entry" ]; then
        echo -e "${RED}Error: Domain '$SINGLE_DOMAIN' not found in configuration${NC}"
        exit 1
    fi

    full_domain="${entry%%:*}"
    expected_ip="${entry##*:}"

    if $VERBOSE; then
        echo "Testing: $full_domain (expected: $expected_ip)"
        echo ""
        echo "Full dig output:"
        dig @"$PI_IP" "$full_domain"
        echo ""
        echo "Result:"
    fi

    if test_dns "$full_domain" "$expected_ip"; then
        ((passed++))
    else
        ((failed++))
    fi
else
    # Test all domains
    while IFS= read -r entry; do
        full_domain="${entry%%:*}"
        expected_ip="${entry##*:}"

        if $VERBOSE; then
            echo "---"
            echo "Testing: $full_domain"
            echo "Expected: $expected_ip"
        fi

        if test_dns "$full_domain" "$expected_ip"; then
            ((passed++))
        else
            ((failed++))
        fi
    done < <(get_domains)
fi

echo ""
echo "========================"
echo -e "Results: ${GREEN}$passed passed${NC}, ${RED}$failed failed${NC}"

if [ $failed -gt 0 ]; then
    echo ""
    echo -e "${YELLOW}To fix failed entries, run:${NC}"
    echo "  cd $PROJECT_DIR && ./scripts/manage-domains.sh apply"
    exit 1
fi

exit 0
