#!/bin/bash

# PaiiD Deployment Verification Script (Bash)
# Comprehensive verification of deployed services

set -e  # Exit on error

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Default values
BACKEND_URL="https://paiid-backend.onrender.com"
FRONTEND_URL="https://paiid-frontend.onrender.com"
VERBOSE=false
TIMEOUT=10

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --backend-url)
            BACKEND_URL="$2"
            shift 2
            ;;
        --frontend-url)
            FRONTEND_URL="$2"
            shift 2
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --backend-url URL     Backend URL (default: $BACKEND_URL)"
            echo "  --frontend-url URL    Frontend URL (default: $FRONTEND_URL)"
            echo "  --verbose            Verbose output"
            echo "  --timeout SECONDS    Request timeout (default: $TIMEOUT)"
            echo "  --help               Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_test() {
    echo -e "${CYAN}[TEST]${NC} $1"
}

# Test result tracking
TESTS_PASSED=0
TESTS_FAILED=0
FAILED_TESTS=()

# Test function
run_test() {
    local test_name="$1"
    local test_url="$2"
    local expected_content="$3"
    local test_description="$4"
    
    log_test "$test_name"
    if [[ "$VERBOSE" == "true" ]]; then
        echo "  URL: $test_url"
        echo "  Expected: $expected_content"
        echo "  Description: $test_description"
    fi
    
    # Make request with timeout
    local response
    local status_code
    local response_time
    
    local start_time=$(date +%s%3N)
    
    if response=$(curl -s -w "\n%{http_code}" --max-time "$TIMEOUT" "$test_url" 2>/dev/null); then
        status_code=$(echo "$response" | tail -n1)
        response_body=$(echo "$response" | head -n -1)
        local end_time=$(date +%s%3N)
        response_time=$((end_time - start_time))
        
        if [[ "$status_code" == "200" ]]; then
            if [[ -n "$expected_content" ]]; then
                if echo "$response_body" | grep -q "$expected_content"; then
                    log_success "✓ $test_name - PASS (${response_time}ms)"
                    ((TESTS_PASSED++))
                    return 0
                else
                    log_error "✗ $test_name - FAIL (content mismatch)"
                    if [[ "$VERBOSE" == "true" ]]; then
                        echo "  Expected: $expected_content"
                        echo "  Got: $response_body"
                    fi
                    ((TESTS_FAILED++))
                    FAILED_TESTS+=("$test_name")
                    return 1
                fi
            else
                log_success "✓ $test_name - PASS (${response_time}ms)"
                ((TESTS_PASSED++))
                return 0
            fi
        else
            log_error "✗ $test_name - FAIL (HTTP $status_code)"
            if [[ "$VERBOSE" == "true" ]]; then
                echo "  Response: $response_body"
            fi
            ((TESTS_FAILED++))
            FAILED_TESTS+=("$test_name")
            return 1
        fi
    else
        log_error "✗ $test_name - FAIL (connection error)"
        ((TESTS_FAILED++))
        FAILED_TESTS+=("$test_name")
        return 1
    fi
}

# Health endpoint tests
test_health_endpoints() {
    log_info "Testing health endpoints..."
    
    run_test "Backend Health" \
        "$BACKEND_URL/api/health" \
        "healthy" \
        "Basic health check"
    
    run_test "Backend Detailed Health" \
        "$BACKEND_URL/api/health/detailed" \
        "status" \
        "Detailed health information"
    
    run_test "Backend Readiness" \
        "$BACKEND_URL/api/health/readiness" \
        "ready" \
        "Readiness check"
    
    run_test "Backend Liveness" \
        "$BACKEND_URL/api/health/liveness" \
        "alive" \
        "Liveness check"
}

# API endpoint tests
test_api_endpoints() {
    log_info "Testing API endpoints..."
    
    run_test "Backend Settings" \
        "$BACKEND_URL/api/settings" \
        "stop_loss" \
        "Settings endpoint"
    
    run_test "Backend Configuration" \
        "$BACKEND_URL/api/settings/config" \
        "environment" \
        "Configuration endpoint"
    
    run_test "Backend Market Conditions" \
        "$BACKEND_URL/api/market/conditions" \
        "conditions" \
        "Market conditions endpoint"
    
    run_test "Backend Market Indices" \
        "$BACKEND_URL/api/market/indices" \
        "dow" \
        "Market indices endpoint"
}

# Frontend tests
test_frontend() {
    log_info "Testing frontend..."
    
    run_test "Frontend Health" \
        "$FRONTEND_URL" \
        "PaiiD" \
        "Frontend homepage"
    
    # Test if frontend is serving static files
    run_test "Frontend Static Assets" \
        "$FRONTEND_URL/_next/static" \
        "" \
        "Static assets directory"
}

# External service tests
test_external_services() {
    log_info "Testing external service connectivity..."
    
    # Test if backend can reach external services
    run_test "Backend External Services" \
        "$BACKEND_URL/api/health/detailed" \
        "external_services" \
        "External service connectivity"
}

# Configuration tests
test_configuration() {
    log_info "Testing configuration..."
    
    # Test configuration endpoint for proper environment
    run_test "Backend Environment" \
        "$BACKEND_URL/api/settings/config" \
        "production" \
        "Production environment configuration"
    
    # Test if Sentry is configured (if in production)
    run_test "Backend Sentry Configuration" \
        "$BACKEND_URL/api/settings/config" \
        "sentry_configured" \
        "Sentry error tracking configuration"
}

# Performance tests
test_performance() {
    log_info "Testing performance..."
    
    # Test response times
    local start_time=$(date +%s%3N)
    if curl -s --max-time "$TIMEOUT" "$BACKEND_URL/api/health" > /dev/null; then
        local end_time=$(date +%s%3N)
        local response_time=$((end_time - start_time))
        
        if [[ $response_time -lt 5000 ]]; then
            log_success "✓ Performance - PASS (${response_time}ms)"
            ((TESTS_PASSED++))
        else
            log_warning "⚠ Performance - SLOW (${response_time}ms)"
            ((TESTS_PASSED++))
        fi
    else
        log_error "✗ Performance - FAIL (timeout)"
        ((TESTS_FAILED++))
        FAILED_TESTS+=("Performance")
    fi
}

# Main verification function
main() {
    log_info "🔍 Starting PaiiD deployment verification..."
    log_info "Backend URL: $BACKEND_URL"
    log_info "Frontend URL: $FRONTEND_URL"
    log_info "Timeout: ${TIMEOUT}s"
    echo ""
    
    # Run all test suites
    test_health_endpoints
    test_api_endpoints
    test_frontend
    test_external_services
    test_configuration
    test_performance
    
    # Generate summary
    echo ""
    log_info "📊 Verification Summary"
    echo "================================"
    log_success "Passed: $TESTS_PASSED"
    if [[ $TESTS_FAILED -gt 0 ]]; then
        log_error "Failed: $TESTS_FAILED"
        log_error "Failed tests: ${FAILED_TESTS[*]}"
    else
        log_success "Failed: $TESTS_FAILED"
    fi
    
    # Overall result
    if [[ $TESTS_FAILED -eq 0 ]]; then
        log_success "🎉 All verification tests passed!"
        exit 0
    else
        log_error "❌ Some verification tests failed"
        exit 1
    fi
}

# Run main function
main "$@"
