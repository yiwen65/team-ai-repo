#!/usr/bin/env python3
"""
sensor_sync_checker.py
检查 ROS2 bag 中多传感器 topic 的时间同步偏移。

Usage:
  python sensor_sync_checker.py /path/to/rosbag.db3 \
    --topics /camera/front/image /lidar/top/points /radar/front/targets \
    --window 0.1

Output:
  各 topic 的 timestamp 统计 + 两两时差分布 + 异常帧列表
"""

import sqlite3
import argparse
from collections import defaultdict
import numpy as np


def read_ros2_bag(bag_path, topics):
    """Read messages from ROS2 sqlite3 bag."""
    conn = sqlite3.connect(bag_path)
    cursor = conn.cursor()
    
    # Get topic IDs
    topic_ids = {}
    for topic in topics:
        cursor.execute(
            "SELECT id FROM topics WHERE name = ?", (topic,)
        )
        row = cursor.fetchone()
        if row:
            topic_ids[topic] = row[0]
        else:
            print(f"Warning: topic {topic} not found in bag")
    
    # Read timestamps (nanosec from message header or log_time)
    data = defaultdict(list)
    for topic, tid in topic_ids.items():
        cursor.execute(
            "SELECT timestamp FROM messages WHERE topic_id = ? ORDER BY timestamp",
            (tid,)
        )
        data[topic] = [row[0] / 1e9 for row in cursor.fetchall()]  # convert to seconds
    
    conn.close()
    return data


def analyze_sync(data, window_sec=0.1):
    """Analyze time sync between topics."""
    topics = list(data.keys())
    
    print("=" * 60)
    print("Sensor Time Sync Analysis")
    print("=" * 60)
    
    # Per-topic statistics
    for topic in topics:
        timestamps = data[topic]
        if not timestamps:
            continue
        diffs = np.diff(timestamps)
        print(f"\n{topic}:")
        print(f"  Messages: {len(timestamps)}")
        print(f"  Duration: {timestamps[-1] - timestamps[0]:.2f}s")
        print(f"  Avg interval: {np.mean(diffs):.4f}s")
        print(f"  Interval std: {np.std(diffs):.4f}s")
        print(f"  Max gap: {np.max(diffs):.4f}s")
    
    # Pairwise sync analysis
    print("\n" + "=" * 60)
    print("Pairwise Sync Offset")
    print("=" * 60)
    
    for i in range(len(topics)):
        for j in range(i + 1, len(topics)):
            t1, t2 = data[topics[i]], data[topics[j]]
            if not t1 or not t2:
                continue
            
            # Find nearest-neighbor offsets
            offsets = []
            bad_pairs = 0
            ptr = 0
            for ts in t1:
                while ptr < len(t2) and t2[ptr] < ts - window_sec:
                    ptr += 1
                if ptr < len(t2) and abs(t2[ptr] - ts) <= window_sec:
                    offsets.append(t2[ptr] - ts)
                else:
                    bad_pairs += 1
            
            if offsets:
                print(f"\n{topics[i]} <-> {topics[j]}:")
                print(f"  Matched pairs: {len(offsets)} / {len(t1)}")
                print(f"  Unmatched: {bad_pairs}")
                print(f"  Mean offset: {np.mean(offsets)*1000:.2f}ms")
                print(f"  Std offset: {np.std(offsets)*1000:.2f}ms")
                print(f"  Max abs offset: {np.max(np.abs(offsets))*1000:.2f}ms")
                
                # Flag if > 50ms
                if np.max(np.abs(offsets)) > 0.05:
                    print(f"  ⚠️  CRITICAL: sync offset exceeds 50ms threshold")


def main():
    parser = argparse.ArgumentParser(description="Check ROS2 sensor time sync")
    parser.add_argument("bag", help="Path to ROS2 bag (sqlite3)")
    parser.add_argument("--topics", nargs="+", required=True, help="Topics to analyze")
    parser.add_argument("--window", type=float, default=0.1, help="Matching window in seconds")
    args = parser.parse_args()
    
    data = read_ros2_bag(args.bag, args.topics)
    analyze_sync(data, args.window)


if __name__ == "__main__":
    main()
