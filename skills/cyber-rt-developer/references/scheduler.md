# 调度器配置与优化

一句话简介：Cyber RT Scheduler 负责任务调度、线程管理和负载均衡，其配置直接影响系统的实时响应能力和资源利用率。

## 核心概念/原理

Cyber RT 采用多线程调度模型，主要包含两种调度器：
- **Classic Scheduler**：基于优先级的抢占式调度，适用于硬实时任务
- **Choreography Scheduler**：基于 Choreography（编排）的调度，将任务绑定到特定 CPU 核心，减少上下文切换

调度策略的核心思想：
- 将 Component 的处理任务分配到不同调度组
- 通过亲和性配置将关键任务绑定到独立 CPU 核心
- 使用协程和线程池减少线程创建销毁开销

## Apollo-Lite 中的实现位置

- 调度器基类：`cyber/scheduler/scheduler.h`
- Classic 实现：`cyber/scheduler/scheduler_classic.cc`
- Choreography 实现：`cyber/scheduler/scheduler_choreography.cc`
- 配置文件：`cyber/conf/scheduler.conf`
- 调度任务：`cyber/scheduler/processor.cc`（处理线程）

## 关键配置参数/接口

`scheduler.conf` 示例配置：

```protobuf
scheduler_conf {
  policy: "choreography"
  choreography_conf {
    processor_num: 8
    affinity: "range"
    cpuset: "0-7"
    processor_policy: "SCHED_FIFO"
    processor_prio: 10
    tasks {
      name: "lidar_driver"
      processor: 0
      prio: 20
    }
    tasks {
      name: "control"
      processor: 7
      prio: 30
    }
  }
}
```

关键参数：
- `policy`：调度策略，可选 `classic` 或 `choreography`
- `processor_num`：调度线程数量
- `affinity`：CPU 亲和性策略（range、auto、none）
- `processor_policy`：线程调度策略（SCHED_FIFO、SCHED_RR、SCHED_OTHER）
- `processor_prio`：线程优先级
- `tasks`：任务到 CPU 核心的绑定配置

## 常见问题与排查

**Q: 高负载下任务响应延迟大？**
- 使用 Choreography 策略并绑定关键任务到独立 CPU
- 增加 `processor_num`，但不超过物理 CPU 核心数
- 检查是否存在低优先级任务饿死高优先级任务

**Q: 某个 Component 执行频率不稳定？**
- 检查该 Component 的 Task 优先级是否过低
- 确认没有多个高优先级任务竞争同一个 CPU 核心
- 使用 `cyber_top` 查看各任务的 CPU 占用和执行时间

**Q: 实时性要求高的任务抖动大？**
- 设置 `processor_policy: "SCHED_FIFO"` 并提高 `processor_prio`
- 将任务绑定到隔离的 CPU 核心（通过内核参数 `isolcpus`）
- 关闭系统的超线程（Hyper-Threading）以减少干扰

## 与其他模块的接口关系

- **Component**：Component 的 Proc 函数会被封装为 Task 提交给 Scheduler
- **DAG**：DAG 中的组件配置会传递给 Scheduler 作为调度依据
- **Record**：录制回放时 Scheduler 的负载模式会发生变化，需预留资源
- **Transport**：数据到达事件触发 Component 执行，由 Scheduler 分配线程处理
