#!/bin/bash
# Enhanced Backend Process Cleanup Script
# Integrates with process-manager.sh for robust zombie cleanup
# Version: 2.0.0 - With retry logic, PID file cleanup, and socket handle detection

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
PID_DIR="${PROJECT_ROOT}/backend/.run"
LOG_DIR="${PROJECT_ROOT}/backend/.logs"
PORT="${1:-8001}"
MAX_RETRIES=3
RETRY_DELAYS=(2 4 8)  # Exponential backoff: 2s, 4s, 8s

# Ensure directories exist
mkdir -p "$PID_DIR" "$LOG_DIR"

# Import process manager functions if available
PROCESS_MANAGER="${SCRIPT_DIR}/process-manager.sh"
if [ -f "$PROCESS_MANAGER" ]; then
    source "$PROCESS_MANAGER" 2>/dev/null || true
fi

echo "=================================="
echo "Enhanced Backend Process Cleanup"
echo "=================================="
echo "Target port: $PORT"
echo "PID directory: $PID_DIR"
echo "Max retries: $MAX_RETRIES"
echo ""

# Logging function
log_cleanup() {
    local level=$1
    shift
    local message=$*
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" | tee -a "${LOG_DIR}/cleanup.log"
}

# Function to check if port is in use
check_port() {
    if command -v netstat &> /dev/null; then
        netstat -an | grep ":$PORT " | grep "LISTEN" > /dev/null 2>&1
        return $?
    elif command -v lsof &> /dev/null; then
        lsof -i:$PORT > /dev/null 2>&1
        return $?
    else
        log_cleanup WARN "Neither netstat nor lsof available, cannot check port"
        return 1
    fi
}

# Count processes on port
count_processes() {
    if command -v netstat &> /dev/null; then
        netstat -an | grep ":$PORT " | grep "LISTEN" | wc -l
    else
        echo "0"
    fi
}

# Detect zombie processes (state 'Z')
detect_zombie_processes() {
    log_cleanup INFO "Scanning for zombie processes..."
    
    local zombie_count=0
    
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        # Windows - check for zombie processes using WMIC
        if command -v wmic &> /dev/null; then
            wmic process where "name='python.exe'" get processid,executablepath 2>/dev/null | while read line; do
                if [[ "$line" =~ ^[0-9]+ ]]; then
                    local pid=$(echo "$line" | awk '{print $1}')
                    # Check if process is in zombie state (Windows doesn't have true zombies, but we can check for hung processes)
                    if ! ps -p "$pid" > /dev/null 2>&1; then
                        log_cleanup WARN "Found potential zombie process: PID $pid"
                        zombie_count=$((zombie_count + 1))
                    fi
                fi
            done
        fi
    else
        # Unix/Linux/Mac - check for actual zombie processes
        if command -v ps &> /dev/null; then
            local zombies=$(ps aux | awk '$8 ~ /^Z/ { print $2 }' | wc -l)
            if [ "$zombies" -gt 0 ]; then
                log_cleanup WARN "Found $zombies zombie process(es)"
                ps aux | awk '$8 ~ /^Z/ { print "  Zombie PID: " $2 " (" $11 ")" }'
                zombie_count=$zombies
            fi
        fi
    fi
    
    if [ $zombie_count -eq 0 ]; then
        log_cleanup INFO "No zombie processes detected"
    else
        log_cleanup WARN "Detected $zombie_count zombie process(es)"
    fi
    
    return $zombie_count
}

# Cleanup orphaned PID files BEFORE port cleanup
cleanup_pid_files() {
    log_cleanup INFO "Cleaning up orphaned PID files in $PID_DIR..."

    local cleaned=0
    for pid_file in "${PID_DIR}"/*.pid; do
        if [ ! -f "$pid_file" ]; then
            continue
        fi

        local pid=$(cat "$pid_file" 2>/dev/null || echo "")
        local name=$(basename "$pid_file" .pid)

        if [ -z "$pid" ]; then
            log_cleanup WARN "Empty PID file: $pid_file"
            rm -f "$pid_file"
            cleaned=$((cleaned + 1))
            continue
        fi

        # Check if process is still running
        if ! ps -p "$pid" > /dev/null 2>&1; then
            log_cleanup WARN "Orphaned PID file: $name (PID: $pid no longer running)"
            rm -f "$pid_file"
            cleaned=$((cleaned + 1))
        fi
    done

    log_cleanup INFO "Cleaned up $cleaned orphaned PID file(s)"
}

# Windows-specific orphan detection using WMIC
cleanup_windows_orphans() {
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        log_cleanup INFO "Checking for orphaned uvicorn processes using WMIC..."

        # Find orphaned python.exe processes with uvicorn
        if command -v wmic &> /dev/null; then
            local orphaned_pids=()
            wmic process where "name='python.exe' and commandline like '%uvicorn%'" get processid 2>/dev/null | while read pid; do
                if [ -n "$pid" ] && [ "$pid" != "ProcessId" ]; then
                    orphaned_pids+=("$pid")
                    log_cleanup WARN "Found orphaned uvicorn process: PID $pid"
                fi
            done
            
            # Kill orphaned processes
            for pid in "${orphaned_pids[@]}"; do
                log_cleanup INFO "Killing orphaned uvicorn process: PID $pid"
                taskkill //F //PID $pid 2>/dev/null || log_cleanup WARN "Failed to kill PID $pid"
            done
            
            if [ ${#orphaned_pids[@]} -gt 0 ]; then
                log_cleanup INFO "Cleaned up ${#orphaned_pids[@]} orphaned uvicorn process(es)"
            fi
        fi
        
        # Also check for orphaned PowerShell processes running our commands
        log_cleanup INFO "Checking for orphaned PowerShell processes..."
        if command -v wmic &> /dev/null; then
            wmic process where "name='powershell.exe' and commandline like '%uvicorn%'" get processid 2>/dev/null | while read pid; do
                if [ -n "$pid" ] && [ "$pid" != "ProcessId" ]; then
                    log_cleanup WARN "Found orphaned PowerShell process running uvicorn: PID $pid"
                    taskkill //F //PID $pid 2>/dev/null || true
                fi
            done
        fi
    fi
}

# Check for socket TIME_WAIT state
check_socket_time_wait() {
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        local time_wait_count=$(netstat -an | grep ":$PORT " | grep "TIME_WAIT" | wc -l)
        if [ "$time_wait_count" -gt 0 ]; then
            log_cleanup WARN "Found $time_wait_count socket(s) in TIME_WAIT state on port $PORT"
            log_cleanup INFO "Waiting 5 seconds for TIME_WAIT sockets to expire..."
            sleep 5
        fi
    fi
}

# Kill processes by port with retry and escalation
kill_by_port_with_retry() {
    local retry=0

    while [ $retry -lt $MAX_RETRIES ]; do
        log_cleanup INFO "Cleanup attempt $((retry + 1))/$MAX_RETRIES for port $PORT"

        if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
            # Windows
            log_cleanup INFO "Platform: Windows"

            # Find PIDs listening on port
            local PIDS=$(netstat -ano | grep ":$PORT " | grep "LISTENING" | awk '{print $5}' | sort -u)

            if [ -z "$PIDS" ]; then
                log_cleanup INFO "No processes found on port $PORT"
                return 0
            fi

            local COUNT=$(echo "$PIDS" | wc -l)
            log_cleanup WARN "Found $COUNT process(es) on port $PORT: $(echo $PIDS | tr '\n' ' ')"

            # First attempt: Graceful taskkill
            for PID in $PIDS; do
                log_cleanup INFO "Attempting graceful kill of PID $PID..."
                taskkill //PID $PID 2>/dev/null || log_cleanup WARN "Graceful kill failed for $PID"
            done

            sleep 2

            # Check if still running, escalate to force kill
            PIDS=$(netstat -ano | grep ":$PORT " | grep "LISTENING" | awk '{print $5}' | sort -u)
            if [ -n "$PIDS" ]; then
                log_cleanup WARN "Processes still alive, escalating to force kill..."
                for PID in $PIDS; do
                    log_cleanup INFO "Force killing PID $PID..."
                    taskkill //F //PID $PID 2>/dev/null || log_cleanup ERROR "Force kill failed for $PID"
                done
            fi

            # Check for TIME_WAIT sockets
            check_socket_time_wait

        else
            # Linux/Mac
            log_cleanup INFO "Platform: Unix-like"

            if command -v lsof &> /dev/null; then
                local PIDS=$(lsof -ti:$PORT 2>/dev/null || echo "")

                if [ -z "$PIDS" ]; then
                    log_cleanup INFO "No processes found on port $PORT"
                    return 0
                fi

                local COUNT=$(echo "$PIDS" | wc -l)
                log_cleanup WARN "Found $COUNT process(es) on port $PORT: $(echo $PIDS | tr '\n' ' ')"

                # First attempt: SIGTERM (graceful)
                for PID in $PIDS; do
                    log_cleanup INFO "Sending SIGTERM to PID $PID..."
                    kill -TERM $PID 2>/dev/null || log_cleanup WARN "SIGTERM failed for $PID"
                done

                sleep 2

                # Check if still running, escalate to SIGKILL
                PIDS=$(lsof -ti:$PORT 2>/dev/null || echo "")
                if [ -n "$PIDS" ]; then
                    log_cleanup WARN "Processes still alive, escalating to SIGKILL..."
                    for PID in $PIDS; do
                        log_cleanup INFO "Sending SIGKILL to PID $PID..."
                        kill -KILL $PID 2>/dev/null || log_cleanup ERROR "SIGKILL failed for $PID"
                    done
                fi
            else
                log_cleanup WARN "lsof not available, using killall python..."
                killall -9 python 2>/dev/null || log_cleanup INFO "No python processes to kill"
            fi
        fi

        # Wait with exponential backoff
        local delay=${RETRY_DELAYS[$retry]}
        log_cleanup INFO "Waiting ${delay}s before verification..."
        sleep $delay

        # Check if port is now free
        if ! check_port; then
            log_cleanup INFO "Port $PORT successfully freed on attempt $((retry + 1))"
            return 0
        fi

        retry=$((retry + 1))
    done

    # Failed after all retries
    return 1
}

# Generate detailed failure report
generate_failure_report() {
    log_cleanup ERROR "Port cleanup FAILED after $MAX_RETRIES attempts"
    echo ""
    echo "======================================"
    echo "CLEANUP FAILURE REPORT"
    echo "======================================"

    local FINAL_COUNT=$(count_processes)
    echo "Port: $PORT"
    echo "Remaining processes: $FINAL_COUNT"
    echo ""

    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        echo "Active connections on port $PORT:"
        netstat -ano | grep ":$PORT " || echo "  (none found via netstat)"
        echo ""

        local PIDS=$(netstat -ano | grep ":$PORT " | grep "LISTENING" | awk '{print $5}' | sort -u)
        if [ -n "$PIDS" ]; then
            echo "Process details:"
            for PID in $PIDS; do
                echo "  PID $PID:"
                wmic process where "processid=$PID" get caption,commandline,creationdate 2>/dev/null || echo "    (process info unavailable)"
            done
        fi

        echo ""
        echo "TIME_WAIT sockets:"
        netstat -an | grep ":$PORT " | grep "TIME_WAIT" || echo "  (none)"

        echo ""
        echo "EMERGENCY CLEANUP OPTIONS:"
        echo "  Option 1 (Nuclear): scripts/emergency-cleanup.ps1 -Port $PORT"
        echo "  Option 2 (Manual):  Open Task Manager -> Kill all 'python.exe' processes"
        echo "  Option 3 (Reboot):  Restart Windows to release socket handles"
        echo "  Option 4 (Switch):  Use alternate port: PORT=8002 npm run dev"
    else
        echo "Active connections on port $PORT:"
        lsof -i:$PORT || netstat -an | grep ":$PORT " || echo "  (none found)"
        echo ""

        echo "EMERGENCY CLEANUP OPTIONS:"
        echo "  Option 1: sudo lsof -ti:$PORT | xargs kill -9"
        echo "  Option 2: sudo fuser -k $PORT/tcp"
        echo "  Option 3: Restart system"
    fi

    echo "======================================"
    echo ""
}

# Main cleanup flow
main() {
    log_cleanup INFO "Starting enhanced cleanup for port $PORT"

    # Phase 1: Detect zombie processes
    detect_zombie_processes

    # Phase 2: Cleanup orphaned PID files
    cleanup_pid_files

    # Phase 3: Windows-specific orphan detection
    cleanup_windows_orphans

    # Phase 4: Kill processes on target port with retry
    if kill_by_port_with_retry; then
        # Success - final verification
        FINAL_COUNT=$(count_processes)

        if [ "$FINAL_COUNT" -eq 0 ]; then
            echo ""
            echo "=================================="
            log_cleanup INFO "SUCCESS: Port $PORT is now free"
            echo "=================================="
            echo ""
            exit 0
        else
            log_cleanup WARN "Port appears free but netstat shows $FINAL_COUNT connections (may be TIME_WAIT)"
            echo ""
            echo "=================================="
            echo "Port $PORT cleaned (with warnings)"
            echo "=================================="
            echo ""
            exit 0
        fi
    else
        # Failed after retries
        generate_failure_report
        exit 1
    fi
}

# Run cleanup
main
