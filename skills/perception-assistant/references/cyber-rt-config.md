# Cyber RT 配置参考

## DAG 文件格式

Cyber RT 使用 DAG 文件定义模块拓扑：

```protobuf
// example.dag
module_config {
  module_library : "/apollo/bazel-bin/modules/perception/libperception.so"
  
  components {
    class_name : "CameraPerceptionComponent"
    config {
      name : "camera_front"
      readers {
        channel: "/apollo/sensor/camera/front_6mm/image"
      }
    }
  }
  
  components {
    class_name : "FusionComponent"
    config {
      name : "fusion"
      readers {
        channel: "/apollo/perception/camera/front_6mm"
      }
      readers {
        channel: "/apollo/perception/lidar/lidar128"
      }
    }
  }
}
```

## Component 类型

| 类型 | 用途 | 触发方式 |
|------|------|---------|
| Component | 通用组件 | 消息触发 |
| TimerComponent | 定时组件 | 定时器触发 |
| NullComponent | 无输入 | 手动触发 |

## QoS 配置

```protobuf
// cyber/conf/cyber_conf.pb.txt
transport_conf {
  shm_conf {
    enable: true          # 共享内存传输
    shm_size: 104857600   # 100MB
  }
  
  rtps_conf {
    enable: true          # DDS RTPS 传输
    network_interface: "eth0"
  }
}
```

## 常用调试命令

```bash
# 查看所有 channel
cyber_channel list

# 查看 channel 信息
cyber_channel info /apollo/perception/obstacles

# 监听 channel 数据
cyber_channel echo /apollo/perception/obstacles

# 录制数据
cyber_recorder record -c /apollo/perception/obstacles

# 回放数据
cyber_recorder play -f record_file.record

# 查看节点
cyber_node list

# 查看节点信息
cyber_node info /perception/camera_front
```

## Channel 命名规范

| 层级 | 命名规则 | 示例 |
|------|---------|------|
| 传感器原始数据 | `/apollo/sensor/{type}/{location}/{detail}` | `/apollo/sensor/camera/front_6mm/image` |
| 感知输出 | `/apollo/perception/{module}/{detail}` | `/apollo/perception/obstacles` |
| 规划输出 | `/apollo/planning/{detail}` | `/apollo/planning/trajectory` |
| 控制输出 | `/apollo/control/{detail}` | `/apollo/control/chassis` |
| 定位输出 | `/apollo/localization/pose` | `/apollo/localization/pose` |

## 常见问题

| 问题 | 诊断 | 修复 |
|------|------|------|
| Component 不启动 | DAG 中 class_name 不匹配 | 检查 so 库中类名 |
| Channel 无数据 | readers/writers channel 名不匹配 | 统一 channel 命名 |
| 消息丢失 | QoS 队列满 | 增大 queue_size |
| 延迟大 | SHM 未启用 | 开启共享内存传输 |
| 多机通信失败 | RTPS 配置错误 | 检查 network_interface |
