#!/usr/bin/env bash
#
# Infrastructure Health Check Script
# Part of infra-manage-ssh-services skill
#
# Usage:
#   bash health_check.sh              # Check all hosts
#   bash health_check.sh infra        # Check specific host
#   bash health_check.sh --verbose    # Verbose output

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
HOSTS=("infra.local" "deus" "homeassistant.local" "pi4-motor.local" "armitage.local")
CRITICAL_SERVICES=("mongodb" "langfuse" "otel-collector")

# Verbose mode
VERBOSE=0
[[ "${1:-}" == "--verbose" ]] && VERBOSE=1

# Target host (if specified)
TARGET_HOST="${1:-all}"

# Helper functions
log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_info() {
    [[ $VERBOSE -eq 1 ]] && echo "   $1"
}

# Test network connectivity
test_ping() {
    local host="$1"
    if ping -c 1 -W 1 "$host" &>/dev/null; then
        log_success "$host is reachable"
        return 0
    else
        log_error "$host is unreachable"
        return 1
    fi
}

# Test SSH connectivity
test_ssh() {
    local host="$1"
    if ssh -o ConnectTimeout=2 -o BatchMode=yes "$host" "echo 'OK'" &>/dev/null; then
        log_success "SSH to $host works"
        return 0
    else
        log_error "SSH to $host failed"
        return 1
    fi
}

# Test specific port
test_port() {
    local host="$1"
    local port="$2"
    local service="${3:-service}"

    if nc -z -w 2 "$host" "$port" &>/dev/null; then
        log_success "$service port $port on $host is open"
        return 0
    else
        log_error "$service port $port on $host is closed"
        return 1
    fi
}

# Check Docker containers on host
check_docker() {
    local host="$1"

    log_info "Checking Docker containers on $host..."

    if ! ssh "$host" "docker ps &>/dev/null" 2>/dev/null; then
        log_warning "Docker not accessible on $host"
        return 1
    fi

    local container_count
    container_count=$(ssh "$host" "docker ps --format '{{.Names}}' 2>/dev/null | wc -l" 2>/dev/null || echo "0")

    if [[ "$container_count" -gt 0 ]]; then
        log_success "$container_count Docker containers running on $host"
        [[ $VERBOSE -eq 1 ]] && ssh "$host" "docker ps --format 'table {{.Names}}\t{{.Status}}'" 2>/dev/null
        return 0
    else
        log_warning "No Docker containers running on $host"
        return 1
    fi
}

# Check specific service health
check_service() {
    local host="$1"
    local service="$2"

    log_info "Checking $service on $host..."

    # Get container name pattern
    local container_pattern
    case "$service" in
        mongodb)
            container_pattern="mongodb"
            ;;
        langfuse)
            container_pattern="langfuse-web"
            ;;
        otel-collector)
            container_pattern="otel-collector"
            ;;
        *)
            log_warning "Unknown service: $service"
            return 1
            ;;
    esac

    # Check if container exists
    local container_id
    container_id=$(ssh "$host" "docker ps -q -f name=$container_pattern" 2>/dev/null || echo "")

    if [[ -z "$container_id" ]]; then
        log_error "$service container not found on $host"
        return 1
    fi

    # Get container status
    local container_name
    container_name=$(ssh "$host" "docker ps --format '{{.Names}}' -f name=$container_pattern" 2>/dev/null || echo "")

    local health_status
    health_status=$(ssh "$host" "docker inspect --format='{{.State.Health.Status}}' $container_name 2>/dev/null || echo 'no-health-check'" 2>/dev/null)

    if [[ "$health_status" == "healthy" ]] || [[ "$health_status" == "no-health-check" ]]; then
        log_success "$service is healthy on $host"
        return 0
    else
        log_warning "$service health status: $health_status on $host"
        return 1
    fi
}

# Check MongoDB specifically
check_mongodb() {
    local host="$1"

    log_info "Testing MongoDB connectivity..."

    # Test port
    if ! test_port "$host" 27017 "MongoDB"; then
        return 1
    fi

    # Test MongoDB ping (MongoDB 4.4 uses 'mongo' not 'mongosh')
    if ssh "$host" "docker exec local-infra-mongodb-1 mongo off --quiet --eval 'db.runCommand({ping: 1}).ok' 2>/dev/null" | grep -q "1"; then
        log_success "MongoDB responds to ping on $host"

        # Get product count if verbose
        if [[ $VERBOSE -eq 1 ]]; then
            local product_count
            product_count=$(ssh "$host" "docker exec local-infra-mongodb-1 mongo off --quiet --eval 'db.products.countDocuments()' 2>/dev/null" || echo "0")
            log_info "MongoDB has $product_count products"
        fi
        return 0
    else
        log_error "MongoDB ping failed on $host"
        return 1
    fi
}

# Check Langfuse specifically
check_langfuse() {
    local host="$1"

    log_info "Testing Langfuse accessibility..."

    # Test HTTP endpoint
    local http_code
    http_code=$(curl -s -o /dev/null -w "%{http_code}" "http://$host:3000" 2>/dev/null || echo "000")

    if [[ "$http_code" == "200" ]] || [[ "$http_code" == "302" ]]; then
        log_success "Langfuse web UI accessible on $host (HTTP $http_code)"
        return 0
    else
        log_error "Langfuse not accessible on $host (HTTP $http_code)"
        return 1
    fi
}

# Check OTLP Collector
check_otlp() {
    local host="$1"

    log_info "Testing OTLP Collector..."

    # Test gRPC port
    if test_port "$host" 4317 "OTLP"; then
        return 0
    else
        return 1
    fi
}

# Main health check for a host
check_host() {
    local host="$1"

    echo ""
    echo "═══════════════════════════════════════"
    echo "Checking: $host"
    echo "═══════════════════════════════════════"

    # Test ping
    if ! test_ping "$host"; then
        log_warning "Skipping remaining checks (host unreachable)"
        return 1
    fi

    # Test SSH
    if ! test_ssh "$host"; then
        log_warning "Skipping Docker checks (SSH failed)"
        return 1
    fi

    # Check Docker
    check_docker "$host" || true

    # For infra.local, check critical services
    if [[ "$host" == "infra.local" ]] || [[ "$host" == "infra" ]]; then
        echo ""
        echo "Critical Services on $host:"
        check_mongodb "$host" || true
        check_langfuse "$host" || true
        check_otlp "$host" || true
    fi

    # For homeassistant.local, check Home Assistant
    if [[ "$host" == "homeassistant.local" ]] || [[ "$host" == "ha" ]]; then
        echo ""
        echo "Home Assistant on $host:"
        test_port "192.168.68.123" 8123 "Home Assistant" || true
    fi

    return 0
}

# Main script
main() {
    echo "╔═══════════════════════════════════════╗"
    echo "║   Infrastructure Health Check        ║"
    echo "╚═══════════════════════════════════════╝"

    if [[ "$TARGET_HOST" == "all" ]]; then
        # Check all hosts
        for host in "${HOSTS[@]}"; do
            check_host "$host" || true
        done
    else
        # Check specific host
        case "$TARGET_HOST" in
            infra)
                check_host "infra.local"
                ;;
            deus)
                check_host "deus"
                ;;
            ha|homeassistant)
                check_host "homeassistant.local"
                ;;
            motor)
                check_host "pi4-motor.local"
                ;;
            armitage)
                check_host "armitage.local"
                ;;
            *)
                check_host "$TARGET_HOST"
                ;;
        esac
    fi

    echo ""
    echo "═══════════════════════════════════════"
    echo "Health check complete!"
    echo "═══════════════════════════════════════"
}

# Run main
main
