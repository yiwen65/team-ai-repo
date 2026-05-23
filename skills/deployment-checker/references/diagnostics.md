# 诊断与监控参考

## ros2 doctor

```bash
# 基础诊断
ros2 doctor --report

# 关键检查项
- ROS_DISTRO 环境变量
- DDS 中间件配置
- 网络接口配置
- 话题/服务/参数发现
- 系统时钟同步
```

## 日志规范

**结构化日志格式**：
```json
{
  "timestamp": "2026-05-23T14:30:00.123Z",
  "level": "ERROR",
  "module": "perception",
  "node": "camera_detector",
  "trace_id": "abc123",
  "message": "Image processing timeout",
  "context": {
    "camera_id": "front",
    "latency_ms": 150,
    "queue_size": 10
  }
}
```

**日志级别使用**：
| 级别 | 使用场景 |
|------|---------|
| DEBUG | 开发调试，生产关闭 |
| INFO | 状态变化、配置加载 |
| WARN | 性能降级、非致命异常 |
| ERROR | 功能失效、需人工介入 |
| FATAL | 系统崩溃、安全相关 |

## 监控指标

| 指标 | 采集方式 | 告警阈值 |
|------|---------|---------|
| 节点心跳 | /diagnostics | > 500ms |
| 话题频率 | ros2 topic hz | 低于预期 20% |
| GPU 利用率 | nvidia-smi | > 90% 持续 1min |
| 内存使用 | /proc/meminfo | > 90% |
| 磁盘空间 | df -h | > 85% |
| CPU 温度 | sensors | > 85°C |

## systemd 服务管理

```ini
# /etc/systemd/system/autoware.service
[Unit]
Description=Autoware Drive Stack
After=network.target nvidia-persistenced.service

[Service]
Type=simple
User=autoware
ExecStart=/opt/autoware/start_stack.sh
Restart=on-failure
RestartSec=5
Environment="ROS_DOMAIN_ID=0"
Environment="CUDA_VISIBLE_DEVICES=0"

# 资源限制
LimitNOFILE=65536
MemoryMax=8G
CPUQuota=800%

[Install]
WantedBy=multi-user.target
```

## 常用诊断命令

```bash
# 节点拓扑
ros2 node list
ros2 topic list -t
rqt_graph

# 消息检查
ros2 topic echo /camera/front/image_raw --once
ros2 topic hz /camera/front/image_raw

# 包录制/回放
ros2 bag record -a
ros2 bag play recording.bag

# 性能
ros2 run rqt_top rqt_top  # CPU/内存
nvidia-smi dmon  # GPU 监控
```
