# Channel QoS 配置

一句话简介：Channel QoS（服务质量）配置控制 Cyber RT 中消息传输的可靠性、延迟和带宽资源分配，直接影响系统实时性和稳定性。

## 核心概念/原理

Cyber RT 基于 DDS 的 QoS 模型，为每个 Channel 的 Reader 和 Writer 提供可配置的服务质量参数。主要策略包括：
- **Reliability**：可靠传输（RELIABLE）或尽力而为（BEST_EFFORT）
- **Durability**：消息持久化策略，控制历史数据保留
- **History**：队列深度策略，控制缓存消息数量
- **Deadline**：数据到达的最大允许延迟

不同模块对 QoS 的要求不同：感知模块通常使用 BEST_EFFORT 以降低延迟，规划控制模块使用 RELIABLE 以保证指令不丢失。

## Apollo-Lite 中的实现位置

- QoS 定义：`cyber/transport/qos/qos_profile_conf.h`
- 默认配置：`cyber/conf/cyber.pb.conf`
- RTPS 实现：`cyber/transport/rtps/` 下的 QoS 映射
- SHM 实现：`cyber/transport/shm/` 下的缓冲区管理

## 关键配置参数/接口

```protobuf
qos_profile {
  history: KEEP_LAST
  depth: 10
  reliability: RELIABLE
  durability: VOLATILE
  deadline_ms: 100
}
```

参数说明：
- `history`：KEEP_LAST（保留最新 N 条）或 KEEP_ALL（保留所有）
- `depth`：KEEP_LAST 模式下的队列深度
- `reliability`：RELIABLE（确保送达）或 BEST_EFFORT（可能丢包）
- `durability`：VOLATILE（不保留历史）或 TRANSIENT_LOCAL（保留历史给新订阅者）
- `deadline_ms`：数据到达的截止时间

常用 Channel 的推荐配置：
- `/apollo/localization/pose`：RELIABLE, depth=1, deadline=50ms
- `/apollo/sensor/lidar`：BEST_EFFORT, depth=2, deadline=100ms
- `/apollo/control`：RELIABLE, depth=1, deadline=20ms

## 常见问题与排查

**Q: 消息延迟高？**
- 检查 History 策略是否为 KEEP_ALL，改为 KEEP_LAST 并减小 depth
- 确认 reliability 不是 RELIABLE（可靠传输会增加确认开销）
- 检查 `deadline_ms` 是否设置过短导致频繁超时重传

**Q: 新订阅者收不到历史数据？**
- 将 durability 改为 TRANSIENT_LOCAL
- 确保 Writer 的 durability 也设置为相同策略
- 注意：TRANSIENT_LOCAL 会占用更多内存

**Q: 高频消息丢包严重？**
- 增大 depth 以缓存更多消息
- 检查 Subscriber 的处理速度是否跟得上发布频率
- 考虑使用 SHM 传输代替 RTPS 以降低延迟

## 与其他模块的接口关系

- **Transport**：QoS 配置直接映射到底层 RTPS/SHM/Intra 传输的参数
- **DAG 配置**：QoS 在 DAG 文件的 `readers.qos_profile` 中配置
- **Scheduler**：deadline 参数会影响 Scheduler 的任务优先级调整
