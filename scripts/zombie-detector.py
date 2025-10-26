#!/usr/bin/env python3
"""
Zombie Process Detector
Scans for orphaned processes, zombie processes, and port conflicts
Version: 1.0.0
"""

import os
import sys
import psutil
import subprocess
import platform
import json
from typing import List, Dict, Any
from datetime import datetime


class ZombieDetector:
    def __init__(self):
        self.system = platform.system().lower()
        self.expected_ports = [3000, 8001, 8002]
        self.paiid_patterns = [
            "uvicorn",
            "python.*app.main",
            "npm.*dev",
            "next.*dev",
            "paiid",
            "backend",
            "frontend"
        ]
        self.zombies_found = []
        self.orphans_found = []
        self.port_conflicts = []
        
    def detect_zombie_processes(self) -> List[Dict[str, Any]]:
        """Detect actual zombie processes (state 'Z')"""
        zombies = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'status', 'cmdline']):
                try:
                    if proc.info['status'] == psutil.STATUS_ZOMBIE:
                        zombies.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'status': proc.info['status'],
                            'cmdline': ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else 'N/A'
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
        except Exception as e:
            print(f"Error scanning for zombie processes: {e}")
            
        return zombies
    
    def detect_orphaned_processes(self) -> List[Dict[str, Any]]:
        """Detect orphaned processes (no parent or parent is init)"""
        orphans = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'ppid', 'cmdline', 'create_time']):
                try:
                    # Skip system processes
                    if proc.info['pid'] < 10:
                        continue
                        
                    # Check if parent is init (PID 1) or system process
                    ppid = proc.info['ppid']
                    if ppid == 1 or ppid < 10:
                        # Check if this looks like a PaiiD process
                        cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                        if any(pattern.lower() in cmdline.lower() for pattern in self.paiid_patterns):
                            orphans.append({
                                'pid': proc.info['pid'],
                                'name': proc.info['name'],
                                'ppid': ppid,
                                'cmdline': cmdline,
                                'create_time': datetime.fromtimestamp(proc.info['create_time']).isoformat()
                            })
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
        except Exception as e:
            print(f"Error scanning for orphaned processes: {e}")
            
        return orphans
    
    def detect_port_conflicts(self) -> List[Dict[str, Any]]:
        """Detect processes listening on expected ports"""
        conflicts = []
        
        for port in self.expected_ports:
            try:
                connections = []
                for conn in psutil.net_connections(kind='inet'):
                    if conn.laddr.port == port and conn.status == psutil.CONN_LISTEN:
                        try:
                            proc = psutil.Process(conn.pid)
                            connections.append({
                                'pid': conn.pid,
                                'name': proc.name(),
                                'cmdline': ' '.join(proc.cmdline()) if proc.cmdline() else 'N/A',
                                'port': port
                            })
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            connections.append({
                                'pid': conn.pid,
                                'name': 'Unknown',
                                'cmdline': 'N/A',
                                'port': port
                            })
                
                if connections:
                    conflicts.extend(connections)
                    
            except Exception as e:
                print(f"Error checking port {port}: {e}")
                
        return conflicts
    
    def detect_hung_processes(self) -> List[Dict[str, Any]]:
        """Detect potentially hung processes (high CPU but no activity)"""
        hung = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_percent']):
                try:
                    # Check if process matches PaiiD patterns
                    cmdline = ' '.join(proc.cmdline()) if proc.cmdline() else ''
                    if any(pattern.lower() in cmdline.lower() for pattern in self.paiid_patterns):
                        # Check for high resource usage without activity
                        cpu_percent = proc.cpu_percent()
                        memory_percent = proc.memory_percent()
                        
                        # Flag if high CPU usage (might be stuck in loop)
                        if cpu_percent > 50.0:
                            hung.append({
                                'pid': proc.info['pid'],
                                'name': proc.info['name'],
                                'cmdline': cmdline,
                                'cpu_percent': cpu_percent,
                                'memory_percent': memory_percent,
                                'reason': 'High CPU usage'
                            })
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
        except Exception as e:
            print(f"Error scanning for hung processes: {e}")
            
        return hung
    
    def run_detection(self) -> Dict[str, Any]:
        """Run all detection methods and return results"""
        print("🔍 Zombie Process Detection Starting...")
        print(f"System: {self.system}")
        print(f"Expected ports: {self.expected_ports}")
        print("")
        
        # Run all detection methods
        zombies = self.detect_zombie_processes()
        orphans = self.detect_orphaned_processes()
        conflicts = self.detect_port_conflicts()
        hung = self.detect_hung_processes()
        
        # Compile results
        results = {
            'timestamp': datetime.now().isoformat(),
            'system': self.system,
            'zombie_processes': zombies,
            'orphaned_processes': orphans,
            'port_conflicts': conflicts,
            'hung_processes': hung,
            'summary': {
                'zombies': len(zombies),
                'orphans': len(orphans),
                'port_conflicts': len(conflicts),
                'hung': len(hung),
                'total_issues': len(zombies) + len(orphans) + len(conflicts) + len(hung)
            }
        }
        
        return results
    
    def print_results(self, results: Dict[str, Any]):
        """Print formatted results"""
        summary = results['summary']
        
        print("=" * 70)
        print("ZOMBIE PROCESS DETECTION RESULTS")
        print("=" * 70)
        print(f"Timestamp: {results['timestamp']}")
        print(f"System: {results['system']}")
        print("")
        
        # Zombie processes
        if results['zombie_processes']:
            print(f"🚨 ZOMBIE PROCESSES ({summary['zombies']}):")
            for zombie in results['zombie_processes']:
                print(f"  PID {zombie['pid']}: {zombie['name']} ({zombie['status']})")
                print(f"    Command: {zombie['cmdline']}")
            print("")
        else:
            print("✅ No zombie processes detected")
            print("")
        
        # Orphaned processes
        if results['orphaned_processes']:
            print(f"👻 ORPHANED PROCESSES ({summary['orphans']}):")
            for orphan in results['orphaned_processes']:
                print(f"  PID {orphan['pid']}: {orphan['name']} (PPID: {orphan['ppid']})")
                print(f"    Command: {orphan['cmdline']}")
                print(f"    Created: {orphan['create_time']}")
            print("")
        else:
            print("✅ No orphaned processes detected")
            print("")
        
        # Port conflicts
        if results['port_conflicts']:
            print(f"🔌 PORT CONFLICTS ({summary['port_conflicts']}):")
            for conflict in results['port_conflicts']:
                print(f"  Port {conflict['port']}: PID {conflict['pid']} ({conflict['name']})")
                print(f"    Command: {conflict['cmdline']}")
            print("")
        else:
            print("✅ No port conflicts detected")
            print("")
        
        # Hung processes
        if results['hung_processes']:
            print(f"⏰ HUNG PROCESSES ({summary['hung']}):")
            for hung in results['hung_processes']:
                print(f"  PID {hung['pid']}: {hung['name']} ({hung['reason']})")
                print(f"    CPU: {hung['cpu_percent']:.1f}%, Memory: {hung['memory_percent']:.1f}%")
                print(f"    Command: {hung['cmdline']}")
            print("")
        else:
            print("✅ No hung processes detected")
            print("")
        
        # Summary
        print("=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"Total issues found: {summary['total_issues']}")
        if summary['total_issues'] == 0:
            print("🎉 System is clean - no zombie processes detected!")
        else:
            print("⚠️  Issues detected - consider running cleanup scripts")
        print("=" * 70)


def main():
    """Main entry point"""
    detector = ZombieDetector()
    
    # Run detection
    results = detector.run_detection()
    
    # Print results
    detector.print_results(results)
    
    # Save results to file
    output_file = "zombie-detection-results.json"
    try:
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n📄 Results saved to: {output_file}")
    except Exception as e:
        print(f"Warning: Could not save results to file: {e}")
    
    # Exit with appropriate code
    if results['summary']['total_issues'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
