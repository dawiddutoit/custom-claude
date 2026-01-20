#!/bin/bash
# Home Assistant Health Check Script
# Tests HA availability and API access

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
HA_BASE_URL="${HA_BASE_URL:-http://192.168.68.123:8123}"
HA_DOMAIN="${HA_DOMAIN:-https://ha.temet.ai}"
TIMEOUT=10

# Load .env if available
if [[ -f "/Users/dawiddutoit/projects/play/network-infrastructure/.env" ]]; then
    source "/Users/dawiddutoit/projects/play/network-infrastructure/.env"
fi

# Logging functions
log_success() {
    echo -e "${GREEN}✓${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_info() {
    echo -e "${NC}→${NC} $1"
}

# Check if HA is reachable
check_ha_reachable() {
    log_info "Checking Home Assistant availability..."

    # Direct IP check (bypasses Caddy/Cloudflare)
    if curl -s --max-time "$TIMEOUT" "${HA_BASE_URL}/" | grep -q "Home Assistant"; then
        log_success "Home Assistant responding at ${HA_BASE_URL}"
        return 0
    else
        log_error "Home Assistant not responding at ${HA_BASE_URL}"
        return 1
    fi
}

# Check if HA returns expected 405 for HEAD
check_head_request() {
    log_info "Checking HEAD request behavior (should return 405)..."

    local http_code
    http_code=$(curl -I -s -o /dev/null -w "%{http_code}" --max-time "$TIMEOUT" "${HA_BASE_URL}/" 2>/dev/null || echo "000")

    if [[ "$http_code" == "405" ]]; then
        log_success "HEAD request returns 405 (EXPECTED - HA only supports GET)"
    elif [[ "$http_code" == "200" ]]; then
        log_warning "HEAD request returns 200 (unexpected, but not critical)"
    else
        log_error "HEAD request returns ${http_code} (unexpected)"
        return 1
    fi
}

# Check API access
check_api_access() {
    log_info "Checking Home Assistant API access..."

    if [[ -z "${HA_ACCESS_TOKEN:-}" ]]; then
        log_warning "HA_ACCESS_TOKEN not set - skipping API checks"
        return 0
    fi

    # Test API endpoint
    local api_response
    api_response=$(curl -s --max-time "$TIMEOUT" "${HA_BASE_URL}/api/" \
        -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" 2>/dev/null || echo "")

    if echo "$api_response" | grep -q "API running"; then
        log_success "API access working"
    else
        log_error "API access failed"
        echo "Response: $api_response"
        return 1
    fi
}

# Check API config endpoint
check_api_config() {
    log_info "Checking API configuration endpoint..."

    if [[ -z "${HA_ACCESS_TOKEN:-}" ]]; then
        log_warning "HA_ACCESS_TOKEN not set - skipping config check"
        return 0
    fi

    local config_response
    config_response=$(curl -s --max-time "$TIMEOUT" "${HA_BASE_URL}/api/config" \
        -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" 2>/dev/null || echo "")

    if echo "$config_response" | jq -e '.location_name' >/dev/null 2>&1; then
        local location_name
        location_name=$(echo "$config_response" | jq -r '.location_name')
        log_success "Config endpoint accessible (Location: $location_name)"
    else
        log_error "Config endpoint failed"
        echo "Response: $config_response"
        return 1
    fi
}

# Check domain access (via Caddy/Cloudflare)
check_domain_access() {
    log_info "Checking domain access (${HA_DOMAIN})..."

    # Check if domain resolves
    local http_code
    http_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time "$TIMEOUT" "${HA_DOMAIN}/" 2>/dev/null || echo "000")

    if [[ "$http_code" == "200" ]]; then
        log_success "Domain accessible via ${HA_DOMAIN}"
    elif [[ "$http_code" == "302" ]] || [[ "$http_code" == "303" ]]; then
        log_success "Domain accessible (redirects to auth) via ${HA_DOMAIN}"
    elif [[ "$http_code" == "405" ]]; then
        log_warning "Domain returns 405 (HEAD not supported, but domain is reachable)"
    else
        log_error "Domain not accessible: HTTP ${http_code}"
        return 1
    fi
}

# Check notification service (if configured)
check_notification_service() {
    log_info "Checking notification service..."

    if [[ -z "${HA_ACCESS_TOKEN:-}" ]] || [[ -z "${HA_NOTIFY_SERVICE:-}" ]]; then
        log_warning "Notification service not configured - skipping"
        return 0
    fi

    # List all notify services
    local services
    services=$(curl -s --max-time "$TIMEOUT" "${HA_BASE_URL}/api/services" \
        -H "Authorization: Bearer ${HA_ACCESS_TOKEN}" 2>/dev/null | \
        jq -r '.[] | select(.domain == "notify") | .services | keys[]' 2>/dev/null || echo "")

    local service_name="${HA_NOTIFY_SERVICE#*.}"
    if echo "$services" | grep -q "^${service_name}$"; then
        log_success "Notification service '${HA_NOTIFY_SERVICE}' exists"
    else
        log_error "Notification service '${HA_NOTIFY_SERVICE}' not found"
        echo "Available services:"
        echo "$services" | sed 's/^/  - notify./'
        return 1
    fi
}

# Main health check
main() {
    echo "========================================="
    echo "  Home Assistant Health Check"
    echo "  $(date)"
    echo "========================================="
    echo

    local failures=0

    check_ha_reachable || ((failures++))
    echo

    check_head_request || ((failures++))
    echo

    check_api_access || ((failures++))
    echo

    check_api_config || ((failures++))
    echo

    check_domain_access || ((failures++))
    echo

    check_notification_service || ((failures++))
    echo

    echo "========================================="
    if [[ $failures -eq 0 ]]; then
        log_success "ALL CHECKS PASSED"
        echo "========================================="
        exit 0
    else
        log_error "${failures} CHECK(S) FAILED"
        echo "========================================="
        exit 1
    fi
}

# Run main function
main "$@"
