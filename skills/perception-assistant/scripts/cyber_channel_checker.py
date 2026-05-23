#!/usr/bin/env python3
"""
cyber_channel_checker.py
检查 Cyber RT channel 发布/订阅状态。

Usage:
  python cyber_channel_checker.py \
    --channels /apollo/sensor/camera/front_6mm/image \
             /apollo/perception/obstacles \
             /apollo/planning/trajectory
"""

import subprocess
import argparse
import json
from datetime import datetime


def check_channel(channel):
    """Check channel info using cyber_channel tool."""
    try:
        result = subprocess.run(
            ["cyber_channel", "info", channel],
            capture_output=True, text=True, timeout=5
        )
        
        output = result.stdout
        
        # Parse output
        info = {"channel": channel, "status": "unknown"}
        
        if "publisher" in output.lower() or "writer" in output.lower():
            info["has_publisher"] = True
        if "subscriber" in output.lower() or "reader" in output.lower():
            info["has_subscriber"] = True
            
        if info.get("has_publisher") and info.get("has_subscriber"):
            info["status"] = "✅ healthy"
        elif info.get("has_publisher"):
            info["status"] = "⚠️ no subscribers"
        elif info.get("has_subscriber"):
            info["status"] = "❌ no publisher"
        else:
            info["status"] = "❌ no activity"
            
        return info
    except subprocess.TimeoutExpired:
        return {"channel": channel, "status": "⏱️ timeout"}
    except FileNotFoundError:
        return {"channel": channel, "status": "🔧 cyber_channel not found"}


def main():
    parser = argparse.ArgumentParser(description="Check Cyber RT channel health")
    parser.add_argument("--channels", nargs="+", required=True, help="Channels to check")
    parser.add_argument("--output", help="Output JSON file")
    args = parser.parse_args()
    
    results = []
    for ch in args.channels:
        info = check_channel(ch)
        results.append(info)
        print(f"{info['status']:20s} {info['channel']}")
    
    if args.output:
        with open(args.output, "w") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "channels": results
            }, f, indent=2)


if __name__ == "__main__":
    main()
