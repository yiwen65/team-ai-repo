# Cyber RT 传输层

一句话简介：Cyber RT Transport 层负责消息在进程内/进程间的实际传输，支持 Intra（同一进程）、SHM（共享内存）和 RTPS（DDS 网络）三种传输模式，自动选择最优路径。

## 核心概念/原理

Transport 层是 Cyber RT 的消息通信底座，屏蔽了底层通信细节：

- **IntraDispatcher**：同一进程内的零拷贝消息传递，通过智能指针共享，无序列化开销
- **SHMDispatcher**：同一主机不同进程间的共享内存传输，避免内核态拷贝
- **RTPSDispatcher**：基于 Fast DDS 的网络传输，支持跨主机通信

Dispatcher 根据 Reader 和 Writer 的位置关系自动选择传输方式：
- 同进程 → Intra
- 同主机不同进程 → SHM
- 跨主机 → RTPS

## Apollo-Lite 中的实现位置

- 传输抽象：`cyber/transport/transport.h`
- Intra 分发：`cyber/transport/dispatcher/intra_dispatcher.h`
- SHM 分发：`cyber/transport/dispatcher/shm_dispatcher.h`
- RTPS 分发：`cyber/transport/dispatcher/rtps_dispatcher.h`
- 接收器：`cyber/transport/receiver/` 下的 hybrid/intra/rtps/shm_receiver
- QoS 配置：`cyber/transport/qos/qos_profile_conf.h`
- Protobuf：`cyber/proto/transport_conf.proto`

## 关键配置参数

```protobuf
// transport_conf.proto
transport_conf {
  shm_conf {
    shm_size: 104857600      # 共享内存池大小 (100MB)
    shm_queue_size: 100       # 每 Channel 队列深度
  }
  rtps_conf {
    participant_name: "apollo"
    domain_id: 0
  }
}
```

## 常见问题与排查

| 问题 | 可能原因 | 排查方法 |
|------|---------|---------|
| 跨进程消息丢失 | SHM 队列满 | 增大 `shm_queue_size` 或减少 Publisher 频率 |
| 网络消息延迟高 | RTPS 网络拥塞 | 检查交换机带宽、DDS 发现机制 |
| 同进程消息异常 | Intra 引用计数问题 | 检查消息是否被多线程修改 |
| 传输模式未自动切换 | 拓扑识别失败 | `cyber_monitor` 查看节点分布 |

## 与其他模块的接口

- **Node/Component**：Transport 的上层使用者，通过 Reader/Writer 间接调用
- **Scheduler**：Transport 收到消息后触发 CRoutine 调度
- **Service Discovery**：Transport 依赖 TopologyManager 获取对端地址
