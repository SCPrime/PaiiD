#!/bin/bash
# Universal Process Lifecycle Manager
# Manages PIDs, handles signals, prevents zombies
# Version: 1.0.0

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
PID_DIR="${PROJECT_ROOT}/backend/.run"
LOG_DIR="${PROJECT_ROOT}/backend/.logs"

# Ensure directories exist
mkdir -p "$PID_DIR" "$LOG_DIR"

# Logging functions
log_info() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [INFO] $*" | tee -a "${LOG_DIR}/process-manager.log"
}

log_error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [ERROR] $*" | tee -a "${LOG_DIR}/process-manager.log" >&2
}

log_warn() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [WARN] $*" | tee -a "${LOG_DIR}/process-manager.log"
}

# PID file management
get_pid_file() {
    local name=$1
    echo "${PID_DIR}/${name}.pid"
}

read_pid() {
    local pid_file=$1
    if [ -f "$pid_file" ]; then
        cat "$pid_file"
    else
        echo ""
    fi
}

write_pid() {
    local pid=$1
    local pid_file=$2
    echo "$pid" > "$pid_file"
    log_info "Registered PID $pid in $pid_file"
}

remove_pid() {
    local pid_file=$1
    if [ -f "$pid_file" ]; then
        rm -f "$pid_file"
        log_info "Removed PID file $pid_file"
    fi
}

# Process status checking
is_process_running() {
    local pid=$1
    if [ -z "$pid" ]; then
        return 1
    fi

    if ps -p "$pid" > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Port management
is_port_in_use() {
    local port=$1

    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        # Windows
        netstat -ano | grep ":$port " | grep "LISTENING" > /dev/null 2>&1
    else
        # Unix
        if command -v lsof &> /dev/null; then
            lsof -i:$port > /dev/null 2>&1
        elif command -v netstat &> /dev/null; then
            netstat -an | grep ":$port " | grep "LISTEN" > /dev/null 2>&1
        else
            log_warn "No port checking tool available"
            return 1
        fi
    fi
}

get_port_pid() {
    local port=$1

    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        # Windows
        netstat -ano | grep ":$port " | grep "LISTENING" | awk '{print $5}' | head -1
    else
        # Unix
        if command -v lsof &> /dev/null; then
            lsof -ti:$port | head -1
        else
            echo ""
        fi
    fi
}

# Process termination with escalation
kill_process() {
    local pid=$1
    local timeout=${2:-10}

    if ! is_process_running "$pid"; then
        log_info "Process $pid is not running"
        return 0
    fi

    log_info "Attempting graceful shutdown of PID $pid (SIGTERM)"
    kill -TERM "$pid" 2>/dev/null || true

    # Wait for graceful shutdown
    local waited=0
    while [ $waited -lt $timeout ]; do
        if ! is_process_running "$pid"; then
            log_info "Process $pid terminated gracefully"
            return 0
        fi
        sleep 1
        waited=$((waited + 1))
    done

    # Escalate to SIGKILL
    log_warn "Process $pid did not terminate gracefully, escalating to SIGKILL"
    kill -KILL "$pid" 2>/dev/null || true
    sleep 1

    if ! is_process_running "$pid"; then
        log_info "Process $pid forcefully killed"
        return 0
    else
        log_error "Failed to kill process $pid"
        return 1
    fi
}

# Kill process tree (including children)
kill_process_tree() {
    local pid=$1

    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        # Windows - kill process tree
        taskkill //F //T //PID "$pid" 2>/dev/null || true
    else
        # Unix - find and kill children first
        local children=$(pgrep -P "$pid" 2>/dev/null || true)
        for child in $children; do
            kill_process_tree "$child"
        done
        kill_process "$pid"
    fi
}

# Orphan detection and cleanup
cleanup_orphans() {
    log_info "Scanning for orphaned processes..."

    local cleaned=0
    for pid_file in "${PID_DIR}"/*.pid; do
        if [ ! -f "$pid_file" ]; then
            continue
        fi

        local pid=$(read_pid "$pid_file")
        local name=$(basename "$pid_file" .pid)

        if [ -z "$pid" ]; then
            log_warn "Empty PID file: $pid_file"
            remove_pid "$pid_file"
            continue
        fi

        if ! is_process_running "$pid"; then
            log_warn "Orphaned PID file detected: $name (PID: $pid)"
            remove_pid "$pid_file"
            cleaned=$((cleaned + 1))
        fi
    done

    log_info "Cleaned up $cleaned orphaned PID file(s)"
}

# Port-based cleanup with retry
cleanup_port() {
    local port=$1
    local max_retries=${2:-3}
    local retry=0

    log_info "Cleaning up port $port (max $max_retries retries)"

    while [ $retry -lt $max_retries ]; do
        if ! is_port_in_use "$port"; then
            log_info "Port $port is free"
            return 0
        fi

        local pid=$(get_port_pid "$port")
        if [ -z "$pid" ]; then
            log_warn "Port $port is in use but PID not found"
            retry=$((retry + 1))
            sleep 2
            continue
        fi

        log_info "Port $port is used by PID $pid (attempt $((retry + 1))/$max_retries)"

        if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
            # Windows - use taskkill
            taskkill //F //PID "$pid" 2>/dev/null || true
        else
            # Unix - use kill_process_tree
            kill_process_tree "$pid"
        fi

        sleep 2
        retry=$((retry + 1))
    done

    if is_port_in_use "$port"; then
        log_error "Failed to free port $port after $max_retries attempts"
        return 1
    fi

    log_info "Port $port successfully freed"
    return 0
}

# Start process with registration
start_process() {
    local name=$1
    shift
    local command=$*

    local pid_file=$(get_pid_file "$name")

    # Check if already running
    local existing_pid=$(read_pid "$pid_file")
    if [ -n "$existing_pid" ] && is_process_running "$existing_pid"; then
        log_error "Process $name is already running (PID: $existing_pid)"
        return 1
    fi

    # Clean up stale PID file
    remove_pid "$pid_file"

    # Start process in background
    log_info "Starting process: $name"
    log_info "Command: $command"

    # Execute command and capture PID
    $command &
    local pid=$!

    # Register PID
    write_pid "$pid" "$pid_file"

    # Wait a moment to ensure process started
    sleep 1

    if ! is_process_running "$pid"; then
        log_error "Process $name failed to start"
        remove_pid "$pid_file"
        return 1
    fi

    log_info "Process $name started successfully (PID: $pid)"
    return 0
}

# Stop process with cleanup
stop_process() {
    local name=$1
    local timeout=${2:-10}

    local pid_file=$(get_pid_file "$name")
    local pid=$(read_pid "$pid_file")

    if [ -z "$pid" ]; then
        log_warn "No PID found for $name"
        remove_pid "$pid_file"
        return 0
    fi

    log_info "Stopping process: $name (PID: $pid)"

    if kill_process_tree "$pid" "$timeout"; then
        remove_pid "$pid_file"
        log_info "Process $name stopped successfully"
        return 0
    else
        log_error "Failed to stop process $name"
        return 1
    fi
}

# Status check
status_process() {
    local name=$1

    local pid_file=$(get_pid_file "$name")
    local pid=$(read_pid "$pid_file")

    if [ -z "$pid" ]; then
        echo "Process $name: Not registered"
        return 1
    fi

    if is_process_running "$pid"; then
        echo "Process $name: Running (PID: $pid)"
        return 0
    else
        echo "Process $name: Dead (stale PID: $pid)"
        return 1
    fi
}

# Main command dispatcher
main() {
    local command=${1:-""}
    shift || true

    case "$command" in
        start)
            start_process "$@"
            ;;
        stop)
            stop_process "$@"
            ;;
        restart)
            local name=$1
            shift
            stop_process "$name"
            sleep 2
            start_process "$name" "$@"
            ;;
        status)
            status_process "$@"
            ;;
        cleanup-orphans)
            cleanup_orphans
            ;;
        cleanup-port)
            cleanup_port "$@"
            ;;
        is-running)
            local pid=$1
            if is_process_running "$pid"; then
                exit 0
            else
                exit 1
            fi
            ;;
        *)
            echo "Usage: $0 {start|stop|restart|status|cleanup-orphans|cleanup-port|is-running}"
            echo ""
            echo "Commands:"
            echo "  start <name> <command>        Start a process and register it"
            echo "  stop <name> [timeout]         Stop a registered process"
            echo "  restart <name> <command>      Restart a process"
            echo "  status <name>                 Check process status"
            echo "  cleanup-orphans               Clean up orphaned PID files"
            echo "  cleanup-port <port> [retries] Free a port by killing processes"
            echo "  is-running <pid>              Check if PID is running"
            exit 1
            ;;
    esac
}

# Run main
main "$@"
