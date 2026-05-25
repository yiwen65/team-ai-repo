# Cyber Recorder 数据录制与回放

一句话简介：Cyber Recorder 提供 `.record` 格式的数据录制与回放能力，是 Apollo-Lite 数据闭环、离线调试和场景复现的核心工具。

## 核心概念/原理

Cyber Recorder 使用自定义 `.record` 格式，基于 protobuf 序列化消息，按时间戳顺序存储 Channel 数据。与 ROS bag 不同，`.record` 格式更紧凑，支持消息索引和快速检索。

关键能力：
- **全量录制**：同时录制所有活跃 Channel
- **选择性录制**：指定 Channel 录制，减少数据量
- **倍速回放**：支持 0.1x ~ 10x 倍速回放
- **时间切片**：提取指定时间段的数据
- **消息过滤**：按 Channel 名称或消息大小过滤

## Apollo-Lite 中的实现位置

- Record API：`cyber/record/record_reader.h`、`cyber/record/record_writer.h`
- Record Viewer：`cyber/record/record_viewer.h`
- CLI 工具：`cyber/tools/cyber_recorder/`
- Protobuf 定义：`cyber/proto/record.proto`

## 关键接口与命令

```bash
# 录制
cyber_recorder record -a                          # 录制所有 Channel
cyber_recorder record -c /apollo/perception/obstacles -c /apollo/planning/trajectory

# 回放
cyber_recorder play -f 20260525.record -r 1.0      # 1x 倍速回放
cyber_recorder play -f 20260525.record -s 1000000000  # 从指定时间开始

# 信息查看
cyber_recorder info 20260525.record                # 文件信息、Channel 列表、消息统计

# 切片
cyber_recorder split -f 20260525.record -b 1000000000 -e 2000000000 -o slice.record
```

## 常见问题与排查

| 问题 | 可能原因 | 排查方法 |
|------|---------|---------|
| 录制文件为空 | Channel 未发布数据 | `cyber_channel list` 确认 Channel 活跃 |
| 回放时消息乱序 | 不同 Channel 时间戳未对齐 | 检查各 Publisher 的时钟源是否一致 |
| 回放倍速不生效 | 某些模块依赖实时时钟 | 使用 `-r` 参数而非 `--loop` |
| 文件解析失败 | 版本不兼容或文件损坏 | `cyber_recorder info` 查看头部信息 |

## 与其他模块的接口

- **perception**：录制感知输出用于离线模型验证
- **planning**：回放感知数据，测试规划算法
- **drivers**：录制原始传感器数据，用于驱动调试
- **Guardian/Monitor**：回放安全事件，分析异常场景
