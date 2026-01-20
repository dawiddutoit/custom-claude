#!/bin/bash
# =============================================================================
# Infrastructure Health Check Script
# =============================================================================
# Performs comprehensive health checks on all network infrastructure services.
# Run from: /home/dawiddutoit/projects/network
# Usage: ./scripts/health-check.sh [--quick|--full|--json]
# =============================================================================

set -o pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="/home/dawiddutoit/projects/network"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters for summary
PASS_COUNT=0
FAIL_COUNT=0
WARN_COUNT=0

# Output mode
OUTPUT_MODE="text"  # text, json, or quiet

# Domains to check
HTTPS_DOMAINS=("pihole" "jaeger" "langfuse" "ha" "code")
PROTECTED_DOMAINS=("pihole" "jaeger" "langfuse" "ha" "sprinkler" "code")
HTTP_DOMAINS=("webhook" "sprinkler")

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --quick)
            QUICK_MODE=true
            shift
            ;;
        --full)
            FULL_MODE=true
            shift
            ;;
        --json)
            OUTPUT_MODE="json"
            shift
            ;;
        --quiet|-q)
            OUTPUT_MODE="quiet"
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [--quick|--full|--json|--quiet]"
            echo "  --quick  Skip SSL certificate and Access checks"
            echo "  --full   Include verbose output and all checks"
            echo "  --json   Output results as JSON"
            echo "  --quiet  Only output failures and summary"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Helper functions
print_header() {
    if [[ "$OUTPUT_MODE" == "text" ]]; then
        echo ""
        echo -e "${BLUE}$1${NC}"
        echo "$(echo "$1" | sed 's/./-/g')"
    fi
}

print_pass() {
    ((PASS_COUNT++))
    if [[ "$OUTPUT_MODE" == "text" ]]; then
        echo -e "${GREEN}[PASS]${NC} $1"
    fi
}

print_fail() {
    ((FAIL_COUNT++))
    if [[ "$OUTPUT_MODE" != "json" ]]; then
        echo -e "${RED}[FAIL]${NC} $1"
    fi
}

print_warn() {
    ((WARN_COUNT++))
    if [[ "$OUTPUT_MODE" == "text" ]]; then
        echo -e "${YELLOW}[WARN]${NC} $1"
    fi
}

print_info() {
    if [[ "$OUTPUT_MODE" == "text" && "$FULL_MODE" == "true" ]]; then
        echo -e "${BLUE}[INFO]${NC} $1"
    fi
}

# =============================================================================
# Health Check Functions
# =============================================================================

check_docker_containers() {
    print_header "DOCKER CONTAINERS"

    cd "$PROJECT_DIR" || exit 1

    # Get container statuses
    local containers=("pihole" "caddy" "cloudflared" "webhook")

    for container in "${containers[@]}"; do
        local status
        status=$(docker inspect --format='{{.State.Status}}' "$container" 2>/dev/null)
        local health
        health=$(docker inspect --format='{{if .State.Health}}{{.State.Health.Status}}{{else}}no-healthcheck{{end}}' "$container" 2>/dev/null)

        if [[ "$status" == "running" ]]; then
            if [[ "$health" == "healthy" || "$health" == "no-healthcheck" ]]; then
                print_pass "$container: running${health:+ ($health)}"
            else
                print_warn "$container: running but $health"
            fi
        elif [[ -z "$status" ]]; then
            print_fail "$container: not found"
        else
            print_fail "$container: $status"
        fi
    done
}

check_caddy_https() {
    print_header "HTTPS ENDPOINTS"

    for domain in "${HTTPS_DOMAINS[@]}"; do
        local url="https://${domain}.temet.ai"
        local response
        local http_code

        # Home Assistant doesn't support HEAD requests, use GET instead
        if [[ "$domain" == "ha" ]]; then
            response=$(curl -s "$url" --max-time 5 2>/dev/null | head -1)
            # Check if HTML contains "Home Assistant"
            if echo "$response" | grep -q "Home Assistant"; then
                print_pass "${domain}.temet.ai: HTTP 200 (GET request, HA doesn't support HEAD)"
                continue
            else
                print_fail "${domain}.temet.ai: no valid Home Assistant response"
                continue
            fi
        fi

        # Standard HEAD request for other services
        response=$(curl -sI "$url" --max-time 5 2>/dev/null | head -1)
        http_code=$(echo "$response" | grep -oE "HTTP/[0-9.]+ [0-9]+" | awk '{print $2}')

        if [[ "$http_code" =~ ^(200|302|301|307)$ ]]; then
            print_pass "${domain}.temet.ai: $response"
        elif [[ -z "$http_code" ]]; then
            print_fail "${domain}.temet.ai: no response (timeout or unreachable)"
        else
            print_fail "${domain}.temet.ai: $response"
        fi
    done
}

check_pihole_dns() {
    print_header "DNS RESOLUTION"

    # Check local DNS via Pi-hole
    local local_result
    local_result=$(docker exec pihole dig +short @127.0.0.1 pihole.temet.ai 2>/dev/null | head -1)

    if [[ -n "$local_result" ]]; then
        print_pass "Local DNS (Pi-hole): pihole.temet.ai -> $local_result"
    else
        print_fail "Local DNS (Pi-hole): not resolving"
    fi

    # Check from host
    local host_result
    host_result=$(dig @localhost pihole.temet.ai +short 2>/dev/null | head -1)

    if [[ -n "$host_result" ]]; then
        print_pass "Host DNS: pihole.temet.ai -> $host_result"
    else
        print_warn "Host DNS: not using Pi-hole as resolver"
    fi

    # Check Pi-hole service status
    local pihole_status
    pihole_status=$(docker exec pihole pihole status 2>/dev/null | grep -i "dns service" | head -1)

    if [[ "$pihole_status" =~ "running" ]]; then
        print_pass "Pi-hole DNS service: running"
    else
        print_fail "Pi-hole DNS service: $pihole_status"
    fi
}

check_cloudflare_tunnel() {
    print_header "CLOUDFLARE TUNNEL"

    # Check if cloudflared process is running
    if docker exec cloudflared pgrep -f cloudflared >/dev/null 2>&1; then
        print_pass "Cloudflared process: running"
    else
        print_fail "Cloudflared process: not running"
        return
    fi

    # Check recent logs for connection status
    local tunnel_logs
    tunnel_logs=$(docker logs cloudflared --tail 50 2>&1)

    local connected
    connected=$(echo "$tunnel_logs" | grep -i "registered tunnel connection\|connection.*registered" | tail -1)

    local errors
    errors=$(echo "$tunnel_logs" | grep -iE "error|failed" | tail -3)

    if [[ -n "$connected" ]]; then
        print_pass "Tunnel connection: established"
        if [[ "$FULL_MODE" == "true" ]]; then
            print_info "Last connection: $connected"
        fi
    else
        print_warn "Tunnel connection: no recent connection logs"
    fi

    if [[ -n "$errors" ]]; then
        print_warn "Recent tunnel errors detected (check logs)"
        if [[ "$FULL_MODE" == "true" ]]; then
            echo "$errors" | while read -r line; do
                print_info "  $line"
            done
        fi
    fi
}

check_webhook_endpoint() {
    print_header "WEBHOOK ENDPOINT"

    # Test local webhook
    local local_response
    local_response=$(curl -s http://localhost:9000/hooks/health --max-time 5 2>/dev/null)

    if [[ "$local_response" == "OK" || -n "$local_response" ]]; then
        print_pass "Local webhook (localhost:9000): responding"
    else
        print_fail "Local webhook (localhost:9000): not responding"
    fi

    # Test via domain if tunnel is up
    local domain_response
    domain_response=$(curl -sI https://webhook.temet.ai/hooks/health --max-time 5 2>/dev/null | head -1)
    local http_code
    http_code=$(echo "$domain_response" | grep -oE "HTTP/[0-9.]+ [0-9]+" | awk '{print $2}')

    if [[ "$http_code" =~ ^(200|404)$ ]]; then
        print_pass "Webhook via tunnel: accessible"
    elif [[ -z "$http_code" ]]; then
        print_warn "Webhook via tunnel: not accessible (tunnel may be down)"
    else
        print_fail "Webhook via tunnel: $domain_response"
    fi
}

check_ssl_certificates() {
    if [[ "$QUICK_MODE" == "true" ]]; then
        return
    fi

    print_header "SSL CERTIFICATES"

    for domain in "${HTTPS_DOMAINS[@]}"; do
        local cert_info
        cert_info=$(echo | openssl s_client -servername "${domain}.temet.ai" \
            -connect "${domain}.temet.ai:443" 2>/dev/null | \
            openssl x509 -noout -dates -issuer 2>/dev/null)

        if [[ -z "$cert_info" ]]; then
            print_fail "${domain}.temet.ai: unable to retrieve certificate"
            continue
        fi

        local issuer
        issuer=$(echo "$cert_info" | grep "issuer" | sed 's/issuer=//')
        local not_after
        not_after=$(echo "$cert_info" | grep "notAfter" | sed 's/notAfter=//')

        # Check if certificate expires within 30 days
        local expires_soon
        expires_soon=$(echo | openssl s_client -servername "${domain}.temet.ai" \
            -connect "${domain}.temet.ai:443" 2>/dev/null | \
            openssl x509 -noout -checkend 2592000 2>/dev/null && echo "no" || echo "yes")

        if [[ "$expires_soon" == "yes" ]]; then
            print_warn "${domain}.temet.ai: expires soon ($not_after)"
        else
            # Calculate days remaining
            local exp_epoch
            exp_epoch=$(date -d "$not_after" +%s 2>/dev/null || gdate -d "$not_after" +%s 2>/dev/null)
            local now_epoch
            now_epoch=$(date +%s)
            local days_remaining=$(( (exp_epoch - now_epoch) / 86400 ))

            print_pass "${domain}.temet.ai: valid (${days_remaining} days remaining)"
        fi

        if [[ "$FULL_MODE" == "true" ]]; then
            print_info "  Issuer: $issuer"
            print_info "  Expires: $not_after"
        fi
    done
}

check_cloudflare_access() {
    if [[ "$QUICK_MODE" == "true" ]]; then
        return
    fi

    print_header "CLOUDFLARE ACCESS"

    # Source environment for API credentials
    if [[ -f "$PROJECT_DIR/.env" ]]; then
        source "$PROJECT_DIR/.env"
    fi

    if [[ -z "$CLOUDFLARE_ACCOUNT_ID" || -z "$CLOUDFLARE_ACCESS_API_TOKEN" ]]; then
        print_warn "Cloudflare API credentials not configured, skipping Access check"
        return
    fi

    # Get list of Access applications
    local apps_response
    apps_response=$(curl -s "https://api.cloudflare.com/client/v4/accounts/${CLOUDFLARE_ACCOUNT_ID}/access/apps" \
        -H "Authorization: Bearer ${CLOUDFLARE_ACCESS_API_TOKEN}" 2>/dev/null)

    local success
    success=$(echo "$apps_response" | python3 -c "import sys,json; print(json.load(sys.stdin).get('success', False))" 2>/dev/null)

    if [[ "$success" != "True" ]]; then
        print_fail "Unable to retrieve Cloudflare Access applications"
        return
    fi

    # Check each protected domain
    for domain in "${PROTECTED_DOMAINS[@]}"; do
        local full_domain="${domain}.temet.ai"
        local app_exists
        app_exists=$(echo "$apps_response" | python3 -c "
import sys, json
data = json.load(sys.stdin)
apps = data.get('result', [])
for app in apps:
    if app.get('domain') == '$full_domain':
        print('yes')
        break
else:
    print('no')
" 2>/dev/null)

        if [[ "$app_exists" == "yes" ]]; then
            print_pass "${full_domain}: protected by Access"
        else
            print_warn "${full_domain}: not protected by Access"
        fi
    done

    # Check webhook bypass
    local webhook_domain="webhook.temet.ai"
    local webhook_protected
    webhook_protected=$(echo "$apps_response" | python3 -c "
import sys, json
data = json.load(sys.stdin)
apps = data.get('result', [])
for app in apps:
    if app.get('domain') == '$webhook_domain':
        print('protected')
        break
else:
    print('bypass')
" 2>/dev/null)

    if [[ "$webhook_protected" == "bypass" ]]; then
        print_pass "webhook.temet.ai: bypass (public access)"
    else
        print_warn "webhook.temet.ai: protected (may block GitHub webhooks)"
    fi
}

# =============================================================================
# Main Execution
# =============================================================================

main() {
    if [[ "$OUTPUT_MODE" == "text" ]]; then
        echo "=========================================="
        echo "  Infrastructure Health Report"
        echo "  Generated: $(date '+%Y-%m-%d %H:%M:%S')"
        echo "  Host: $(hostname)"
        echo "=========================================="
    fi

    # Run all checks
    check_docker_containers
    check_caddy_https
    check_pihole_dns
    check_cloudflare_tunnel
    check_webhook_endpoint
    check_ssl_certificates
    check_cloudflare_access

    # Print summary
    if [[ "$OUTPUT_MODE" == "text" ]]; then
        echo ""
        echo "=========================================="
        local total=$((PASS_COUNT + FAIL_COUNT + WARN_COUNT))
        echo "  Summary: $PASS_COUNT passed, $FAIL_COUNT failed, $WARN_COUNT warnings"
        echo "=========================================="

        if [[ $FAIL_COUNT -eq 0 && $WARN_COUNT -eq 0 ]]; then
            echo -e "  ${GREEN}Overall Status: ALL CHECKS PASSED${NC}"
        elif [[ $FAIL_COUNT -eq 0 ]]; then
            echo -e "  ${YELLOW}Overall Status: PASSED WITH WARNINGS${NC}"
        else
            echo -e "  ${RED}Overall Status: FAILURES DETECTED${NC}"
        fi
        echo "=========================================="
    elif [[ "$OUTPUT_MODE" == "json" ]]; then
        cat <<EOF
{
  "timestamp": "$(date -Iseconds)",
  "hostname": "$(hostname)",
  "summary": {
    "passed": $PASS_COUNT,
    "failed": $FAIL_COUNT,
    "warnings": $WARN_COUNT
  },
  "status": "$(if [[ $FAIL_COUNT -eq 0 ]]; then echo "healthy"; else echo "unhealthy"; fi)"
}
EOF
    else
        # Quiet mode - only summary
        if [[ $FAIL_COUNT -gt 0 ]]; then
            echo "UNHEALTHY: $FAIL_COUNT failures, $WARN_COUNT warnings"
            exit 1
        elif [[ $WARN_COUNT -gt 0 ]]; then
            echo "WARNING: $WARN_COUNT warnings"
            exit 0
        else
            echo "HEALTHY"
            exit 0
        fi
    fi

    # Exit with appropriate code
    if [[ $FAIL_COUNT -gt 0 ]]; then
        exit 1
    fi
    exit 0
}

main "$@"
