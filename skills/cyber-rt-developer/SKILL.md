---
name: apollo-cyber-rt-developer
description: >
  Apollo-Lite Cyber RT 中间件深度开发助手。覆盖 Cyber RT 核心子系统开发、Component 编程、
  DAG 配置、Channel QoS、调度策略（Classic/Choreography）、协程（CRoutine）、
  服务发现（Service Discovery）、数据录制回放（Record）、参数服务（Parameter Server）、
  性能调优与调试。在以下场景触发使用：
  (1) Cyber RT Component 开发与调试，(2) DAG/Channel/QoS 配置与排错，
  (3) 调度性能优化（CPU 亲和性、线程池、协程调度），(4) 数据录制与回放（cyber_recorder），
  (5) 节点拓扑与服务发现问题排查，(6) 实时性瓶颈分析（延迟/抖动/丢帧），
  (7) Cyber RT 构建与部署问题。
---

# Apollo Cyber RT Developer

Apollo-Lite Cyber RT 中间件深度开发助手。覆盖 Component/DAG/Channel/Scheduler/Record/Parameter 全链路。

## 快速启动

用户提供以下信息即可触发分析：
- 开发目标（Component/DAG/Channel/Scheduler/Record/Parameter）
- Apollo-lite 路径 + cyber 模块日志
- 代码片段或配置文件（.dag/.launch/.pb.txt）
- 问题描述（启动失败/延迟异常/消息丢失/调度问题）+ 日志

## 核心能力域

| 域 | 说明 | 参考文档 |
|---|---|---|
| Component | Cyber RT 组件开发（普通/定时器）、注册与生命周期 | `references/component-dev.md` |
| DAG | DAG 配置、模块编排、Channel 读写关系 | `references/dag-config.md` |
| Channel | Channel 发布/订阅、QoS 配置、History 策略 | `references/channel-qos.md` |
| Scheduler | Classic/Choreography 调度器、CPU 亲和性、Processor | `references/scheduler.md` |
| CRoutine | 协程创建、挂起/恢复、上下文切换 | `references/croutine.md` |
| Transport | DDS 传输层（RTPS/SHM/Intra）、消息序列化 | `references/transport.md` |
| Record | 数据录制（.record 格式）、回放、切片 | `references/record.md` |
| Parameter | 全局参数服务、动态配置下发 | `references/parameter-server.md` |
| Service Discovery | 节点拓扑自动发现、拓扑变更监听 | `references/service-discovery.md` |

## Cyber RT 架构

```
cyber/
├── component/           # Component 开发框架
│   ├── component.h      # 标准 Component 基类
│   ├── component_base.h # Component 基础接口
│   └── timer_component.h # 定时器 Component
├── node/                # 节点封装
│   ├── node.h           # Node 创建与销毁
│   ├── reader.h         # 消息订阅 Reader
│   └── writer.h         # 消息发布 Writer
├── scheduler/           # 调度器
│   ├── scheduler.h      # 调度器基类
│   ├── policy/          # 调度策略
│   │   ├── classic/     # Classic 策略（线程池）
│   │   └── choreography/ # Choreography 策略（协程编排）
│   └── processor.h      # Processor（执行单元）
├── croutine/            # 协程
│   └── croutine.h       # CRoutine 上下文管理
├── transport/           # 传输层
│   ├── transport.h      # 传输接口
│   ├── dispatcher/      # 消息分发器（RTPS/SHM/Intra）
│   ├── receiver/        # 消息接收器
│   └── qos/             # QoS 配置
├── record/              # 数据录制
│   ├── record_reader.h  # 录制文件读取
│   └── record_writer.h  # 录制文件写入
├── parameter/           # 参数服务
│   ├── parameter_server.h
│   └── parameter_client.h
├── service_discovery/   # 服务发现
│   └── topology_manager.h
├── message/             # 消息处理
│   ├── protobuf_traits.h # Protobuf 序列化
│   └── raw_message.h    # 原始消息
├── timer/               # 定时器
│   ├── timer.h          # 定时器 API
│   └── timing_wheel.h   # 时间轮实现
├── mainboard/           # 主控板
│   ├── mainboard.cc     # 进程入口
│   └── module_controller.h # 模块控制器
├── tools/               # CLI 工具
│   ├── cyber_channel/   # channel 管理
│   ├── cyber_launch/    # launch 管理
│   ├── cyber_monitor/   # 系统监控
│   ├── cyber_node/      # 节点管理
│   ├── cyber_recorder/  # 录制回放
│   └── cyber_service/   # 服务管理
└── proto/               # Cyber RT Protobuf
    ├── dag_conf.proto   # DAG 配置
    ├── qos_profile.proto # QoS 配置
    ├── scheduler_conf.proto # 调度器配置
    └── record.proto     # 录制格式
```

## Component 开发模板

```cpp
// 标准 Component（消息驱动）
#include "cyber/component/component.h"
#include "modules/common_msgs/sensor_msgs/pointcloud.pb.h"

namespace apollo {
namespace perception {

class LidarComponent : public cyber::Component<PointCloud> {
 public:
  bool Init() override;
  bool Proc(const std::shared_ptr<PointCloud>& msg) override;
};

CYBER_REGISTER_COMPONENT(LidarComponent)

}  // namespace perception
}  // namespace apollo
```

```cpp
// 定时器 Component（周期执行）
#include "cyber/component/timer_component.h"

class TimerExample : public cyber::TimerComponent {
 public:
  bool Init() override;
  bool Proc() override;  // 无输入，按固定周期调用
};

CYBER_REGISTER_COMPONENT(TimerExample)
```

## DAG 配置规范

```protobuf
// example.dag
module_config {
  module_library: "bazel-bin/modules/perception/liblidar_component.so"
  components {
    class_name: "LidarComponent"
    config {
      name: "lidar_detection"
      readers {
        channel: "/apollo/sensor/lidar128/compensator/PointCloud2"
      }
      writers {
        channel: "/apollo/perception/obstacles"
      }
    }
  }
}
```

## QoS 配置

```protobuf
// qos_profile.proto 映射
qos_profile {
  history: KEEP_LAST       # KEEP_LAST / KEEP_ALL
  depth: 10               # 历史消息缓存深度
  reliability: RELIABLE   # RELIABLE / BEST_EFFORT
  durability: VOLATILE    # VOLATILE / TRANSIENT_LOCAL
}
```

## 调度器配置

```protobuf
// scheduler_conf.proto
scheduler_conf {
  policy: "choreography"   # "classic" 或 "choreography"
  
  # Classic 策略参数
  classic_conf {
    cpu_sets: "0-7"
    thread_pool_size: 16
  }
  
  # Choreography 策略参数
  choreography_conf {
    cpu_sets: "0-7"
    processor_num: 16
    routine_capacity: 1024
  }
}
```

## Cyber Recorder 深度使用

```bash
# 录制
# -a: 所有 channel
# -c: 指定 channel
# -i: 消息大小过滤
cyber_recorder record -a
cyber_recorder record -c /apollo/perception/obstacles -c /apollo/planning/trajectory

# 回放
# -f: 文件
# -r: 倍速
# -s: 起始时间
cyber_recorder play -f 20260524.record -r 1.0

# 信息查看
cyber_recorder info 20260524.record

# 切片（提取指定时间段/channel）
cyber_recorder split -f 20260524.record -b 1000000000 -e 2000000000 \
  -c /apollo/perception/obstacles -o sliced.record
```

## 问题诊断流程

1. **确认 Cyber RT 启动状态** → `cyber_launch status`
2. **检查 DAG 配置** → class_name 与 so 路径匹配、channel 名称拼写
3. **验证 QoS 兼容性** → Publisher/Subscriber QoS 必须兼容（Reliability/History）
4. **排查调度问题** → `cyber_monitor` 查看 Processor 负载、CRoutine 堆积
5. **分析消息延迟** → `cyber_channel info /apollo/...` 查看频率与延迟
6. **检查录制文件** → `cyber_recorder info` 验证 channel 完整性和时间戳

## 工具命令速查

| 命令 | 用途 |
|------|------|
| `cyber_launch start <dag>` | 启动 DAG |
| `cyber_launch stop <dag>` | 停止 DAG |
| `cyber_launch status` | 查看所有模块状态 |
| `cyber_channel list` | 列出所有 channel |
| `cyber_channel info <ch>` | 查看 channel 详情 |
| `cyber_channel echo <ch>` | 实时监听 channel |
| `cyber_node list` | 列出所有节点 |
| `cyber_node info <node>` | 查看节点详情 |
| `cyber_monitor` | 系统资源与拓扑监控 |
| `cyber_recorder record -a` | 录制所有 channel |
| `cyber_recorder play -f <file>` | 回放录制文件 |
| `cyber_recorder info <file>` | 查看录制文件信息 |

## 输出规范

```markdown
# Cyber RT 开发/调试报告

## 1. 环境基线
## 2. DAG/Component 配置分析
## 3. Channel/QoS 状态
## 4. 调度器性能分析
## 5. 消息延迟与丢帧
## 6. 录制数据完整性
## 7. 根因定位
## 8. 修复方案与验证
```

## 关键原则

- **Component 必须注册**：`CYBER_REGISTER_COMPONENT` 缺失会导致 DAG 加载失败
- **DAG class_name 必须与 so 符号匹配**：so 编译产物中的符号名必须与 DAG 配置完全一致
- **QoS 必须 Publisher/Subscriber 兼容**：Publisher RELIABLE + Subscriber BEST_EFFORT 可以工作，反之不行
- **Choreography 适合确定性场景**： Choreography 调度器对实时性更友好，但配置更复杂
- **Classic 适合通用场景**： Classic 调度器基于线程池，配置简单，适合大多数模块
- **Record 文件是 .record 格式**：不是 ROS bag，需使用 `cyber_recorder` 或 Cyber Record API 处理
- **channel 名称拼写错误是头号故障**：`writers.channel` 与下游 `readers.channel` 必须完全一致
- **Processor 数量不要超过 CPU 核心数**： oversubscription 会导致上下文切换开销剧增
