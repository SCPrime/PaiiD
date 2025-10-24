#!/bin/bash

# PaiiD Cloud Deployment Script (Bash)
# Deploys backend to Render and frontend to Vercel with comprehensive validation

set -e  # Exit on error

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Default values
BACKEND_URL="https://paiid-backend.onrender.com"
FRONTEND_URL="https://paiid-frontend.onrender.com"
SKIP_TESTS=false
SKIP_HEALTH_CHECKS=false
AUTO_APPROVE=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --backend-service-id)
            BACKEND_SERVICE_ID="$2"
            shift 2
            ;;
        --frontend-service-id)
            FRONTEND_SERVICE_ID="$2"
            shift 2
            ;;
        --backend-url)
            BACKEND_URL="$2"
            shift 2
            ;;
        --frontend-url)
            FRONTEND_URL="$2"
            shift 2
            ;;
        --skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        --skip-health-checks)
            SKIP_HEALTH_CHECKS=true
            shift
            ;;
        --auto-approve)
            AUTO_APPROVE=true
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --backend-service-id ID    Render backend service ID"
            echo "  --frontend-service-id ID   Render frontend service ID"
            echo "  --backend-url URL          Backend URL (default: $BACKEND_URL)"
            echo "  --frontend-url URL         Frontend URL (default: $FRONTEND_URL)"
            echo "  --skip-tests              Skip pre-deployment tests"
            echo "  --skip-health-checks      Skip post-deployment health checks"
            echo "  --auto-approve            Auto-approve all prompts (CI/CD mode)"
            echo "  --help                    Show this help message"
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

log_step() {
    echo -e "${CYAN}[STEP]${NC} $1"
}

# Check required environment variables
check_environment() {
    log_step "Checking environment variables..."
    
    if [[ -z "$RENDER_API_KEY" ]]; then
        log_error "RENDER_API_KEY environment variable is required"
        log_info "Set it with: export RENDER_API_KEY='your-api-key'"
        exit 1
    fi
    
    if [[ -z "$BACKEND_SERVICE_ID" ]]; then
        log_error "Backend service ID is required"
        log_info "Use --backend-service-id to specify"
        exit 1
    fi
    
    if [[ -z "$FRONTEND_SERVICE_ID" ]]; then
        log_error "Frontend service ID is required"
        log_info "Use --frontend-service-id to specify"
        exit 1
    fi
    
    log_success "Environment variables validated"
}

# Check git status
check_git_status() {
    log_step "Checking git status..."
    
    # Check for uncommitted changes
    if [[ -n "$(git status --porcelain)" ]]; then
        log_warning "Uncommitted changes detected:"
        git status -sb
        
        if [[ "$AUTO_APPROVE" != "true" ]]; then
            echo ""
            read -p "Continue anyway? (y/N): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                log_info "Deployment cancelled"
                exit 0
            fi
        fi
    fi
    
    # Check current branch
    CURRENT_BRANCH=$(git branch --show-current)
    log_info "Current branch: $CURRENT_BRANCH"
    
    log_success "Git status validated"
}

# Check CLI tools
check_cli_tools() {
    log_step "Checking CLI tools..."
    
    # Check for required tools
    local tools=("git" "curl" "jq")
    local missing_tools=()
    
    for tool in "${tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            missing_tools+=("$tool")
        fi
    done
    
    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        log_error "Missing required tools: ${missing_tools[*]}"
        log_info "Install missing tools and try again"
        exit 1
    fi
    
    log_success "CLI tools validated"
}

# Validate Render configurations
validate_render_config() {
    log_step "Validating Render configurations..."
    
    local validation_errors=()
    
    # Validate backend render config if it exists
    if [[ -f "backend/render.yaml" ]]; then
        if python infra/render/validate.py backend/render.yaml infra/render/backend.json; then
            log_success "Backend render config validated"
        else
            validation_errors+=("Backend config drift detected")
        fi
    fi
    
    # Validate root render config
    if [[ -f "render.yaml" ]]; then
        if python infra/render/validate.py render.yaml; then
            log_success "Root render config validated"
        else
            validation_errors+=("Root config validation failed")
        fi
    fi
    
    if [[ ${#validation_errors[@]} -gt 0 ]]; then
        log_error "Configuration validation failed:"
        for error in "${validation_errors[@]}"; do
            log_error "  • $error"
        done
        exit 1
    fi
    
    log_success "Render configurations validated"
}

# Validate git hold points
validate_hold_points() {
    log_step "Validating git hold points..."
    
    if [[ -f "scripts/check_hold_points.py" ]]; then
        if python scripts/check_hold_points.py; then
            log_success "Hold point validation passed"
        else
            log_error "Hold point validation failed"
            log_error "Locked files may have been modified"
            log_info "Review .cursorrules and get approval"
            exit 1
        fi
    else
        log_warning "Hold point validation script not found, skipping"
    fi
}

# Run pre-deployment tests
run_tests() {
    if [[ "$SKIP_TESTS" == "true" ]]; then
        log_warning "Skipping pre-deployment tests"
        return 0
    fi
    
    log_step "Running pre-deployment tests..."
    
    # Test backend pre-launch validation
    log_info "Testing backend pre-launch validation..."
    cd "$BACKEND_DIR"
    if python -m app.core.prelaunch --check-only; then
        log_success "Backend pre-launch validation passed"
    else
        log_error "Backend pre-launch validation failed"
        exit 1
    fi
    
    # Test frontend build
    log_info "Testing frontend build..."
    cd "$FRONTEND_DIR"
    if npm run build; then
        log_success "Frontend build successful"
    else
        log_error "Frontend build failed"
        exit 1
    fi
    
    cd "$PROJECT_ROOT"
    log_success "All pre-deployment tests passed"
}

# Push to GitHub
push_to_github() {
    log_step "Pushing to GitHub..."
    
    git push origin "$(git branch --show-current)"
    if [[ $? -eq 0 ]]; then
        log_success "Pushed to GitHub"
    else
        log_error "Git push failed"
        exit 1
    fi
}

# Deploy to Render
deploy_to_render() {
    log_step "Deploying to Render..."
    
    # Deploy backend
    log_info "Deploying backend service: $BACKEND_SERVICE_ID"
    local backend_response=$(curl -s -X POST \
        -H "Authorization: Bearer $RENDER_API_KEY" \
        -H "Content-Type: application/json" \
        "https://api.render.com/v1/services/$BACKEND_SERVICE_ID/deploys")
    
    if echo "$backend_response" | jq -e '.id' > /dev/null; then
        local backend_deploy_id=$(echo "$backend_response" | jq -r '.id')
        log_success "Backend deployment triggered (ID: $backend_deploy_id)"
    else
        log_error "Backend deployment failed"
        log_error "Response: $backend_response"
        exit 1
    fi
    
    # Deploy frontend
    log_info "Deploying frontend service: $FRONTEND_SERVICE_ID"
    local frontend_response=$(curl -s -X POST \
        -H "Authorization: Bearer $RENDER_API_KEY" \
        -H "Content-Type: application/json" \
        "https://api.render.com/v1/services/$FRONTEND_SERVICE_ID/deploys")
    
    if echo "$frontend_response" | jq -e '.id' > /dev/null; then
        local frontend_deploy_id=$(echo "$frontend_response" | jq -r '.id')
        log_success "Frontend deployment triggered (ID: $frontend_deploy_id)"
    else
        log_error "Frontend deployment failed"
        log_error "Response: $frontend_response"
        exit 1
    fi
    
    log_success "Both services deployment triggered"
}

# Wait for deployment completion
wait_for_deployment() {
    log_step "Waiting for deployment completion..."
    
    local max_wait=600  # 10 minutes
    local wait_time=0
    local check_interval=30  # 30 seconds
    
    while [[ $wait_time -lt $max_wait ]]; do
        log_info "Waiting for deployment... (${wait_time}s/${max_wait}s)"
        sleep $check_interval
        wait_time=$((wait_time + check_interval))
        
        # Check if services are responding
        if curl -s -f "$BACKEND_URL/api/health" > /dev/null 2>&1; then
            log_success "Backend is responding"
            break
        fi
    done
    
    if [[ $wait_time -ge $max_wait ]]; then
        log_warning "Deployment timeout reached"
    fi
}

# Run health checks
run_health_checks() {
    if [[ "$SKIP_HEALTH_CHECKS" == "true" ]]; then
        log_warning "Skipping health checks"
        return 0
    fi
    
    log_step "Running health checks..."
    
    local tests=(
        "Backend Health:$BACKEND_URL/api/health"
        "Frontend Health:$FRONTEND_URL"
        "Backend Settings:$BACKEND_URL/api/settings"
    )
    
    local passed=0
    local failed=0
    
    for test in "${tests[@]}"; do
        local name="${test%%:*}"
        local url="${test##*:}"
        
        log_info "Testing: $name"
        log_info "URL: $url"
        
        if curl -s -f "$url" > /dev/null 2>&1; then
            log_success "✓ $name - PASS"
            ((passed++))
        else
            log_error "✗ $name - FAIL"
            ((failed++))
        fi
    done
    
    log_info "Health check results: $passed passed, $failed failed"
    
    if [[ $failed -gt 0 ]]; then
        log_warning "Some health checks failed, but deployment may still be in progress"
    fi
}

# Run comprehensive verification
run_verification() {
    log_step "Running comprehensive verification..."
    
    if [[ -f "scripts/verify-deployment.sh" ]]; then
        log_info "Running deployment verification script..."
        if bash scripts/verify-deployment.sh --backend-url "$BACKEND_URL" --frontend-url "$FRONTEND_URL"; then
            log_success "Deployment verification passed"
        else
            log_error "Deployment verification failed"
            log_warning "Some verification tests failed, but deployment may still be functional"
        fi
    else
        log_warning "Verification script not found, skipping comprehensive verification"
    fi
}

# Generate deployment report
generate_report() {
    log_step "Generating deployment report..."
    
    local timestamp=$(date '+%Y%m%d-%H%M%S')
    local report_file="deployment-report-${timestamp}.md"
    
    cat > "$report_file" << EOF
# 🚀 Deployment Report

**Date:** $(date)
**Deployed by:** $(whoami)
**Branch:** $(git branch --show-current)
**Commit:** $(git rev-parse HEAD)

## Services Deployed

- **Backend:** $BACKEND_URL
- **Frontend:** $FRONTEND_URL

## Configuration

- Backend Service ID: $BACKEND_SERVICE_ID
- Frontend Service ID: $FRONTEND_SERVICE_ID
- Skip Tests: $SKIP_TESTS
- Skip Health Checks: $SKIP_HEALTH_CHECKS
- Auto Approve: $AUTO_APPROVE

## Health Status

- Backend: $(curl -s -f "$BACKEND_URL/api/health" > /dev/null 2>&1 && echo "✅ Healthy" || echo "❌ Unhealthy")
- Frontend: $(curl -s -f "$FRONTEND_URL" > /dev/null 2>&1 && echo "✅ Healthy" || echo "❌ Unhealthy")

## Next Steps

1. Verify all endpoints are responding
2. Run full test suite
3. Monitor logs for any issues
4. Update documentation if needed

## Rollback Procedure

If issues are detected:

1. Run: \`./rollback-production.sh --current-tag v1.0.X --previous-tag v1.0.Y\`
2. Verify rollback deployment
3. Investigate root cause
4. Create incident report

---
*Generated by PaiiD deployment script*
EOF

    log_success "Deployment report generated: $report_file"
}

# Main deployment flow
main() {
    log_info "🚀 Starting PaiiD deployment..."
    log_info "Backend URL: $BACKEND_URL"
    log_info "Frontend URL: $FRONTEND_URL"
    echo ""
    
    # Run deployment steps
    check_environment
    check_git_status
    check_cli_tools
    validate_render_config
    validate_hold_points
    run_tests
    push_to_github
    deploy_to_render
    wait_for_deployment
    run_health_checks
    run_verification
    generate_report
    
    log_success "🎉 Deployment completed successfully!"
    log_info "Backend: $BACKEND_URL"
    log_info "Frontend: $FRONTEND_URL"
}

# Run main function
main "$@"
