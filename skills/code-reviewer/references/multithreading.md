# 多线程审查参考

## 竞态条件检测

**常见模式**：
```cpp
// ❌ 竞态条件：非原子读写
bool ready_ = false;
void thread1() { ready_ = true; }
void thread2() { while (!ready_) {} }  // 可能永远循环

// ✅ 原子变量
std::atomic<bool> ready_{false};
void thread1() { ready_.store(true, std::memory_order_release); }
void thread2() { while (!ready_.load(std::memory_order_acquire)) {} }
```

## 死锁预防

** Coffman 条件**：互斥、占有等待、不可抢占、循环等待

**预防策略**：
- 统一加锁顺序：所有线程按 `lockA → lockB` 顺序
- 超时锁：`std::timed_mutex` + `try_lock_for`
- 无锁设计：`std::atomic` + CAS 循环

```cpp
// 推荐：std::lock 同时加锁（避免死锁）
std::mutex m1, m2;
{
    std::lock(m1, m2);  // 原子同时加锁
    std::lock_guard<std::mutex> lg1(m1, std::adopt_lock);
    std::lock_guard<std::mutex> lg2(m2, std::adopt_lock);
    // ...
}
```

## 自动驾驶常见并发模式

**生产者-消费者（传感器 → 处理）**：
```cpp
// 推荐：无锁队列
#include <boost/lockfree/spsc_queue.hpp>

boost::lockfree::spsc_queue<SensorData, boost::lockfree::capacity<1024>> queue_;

// 生产者（中断/回调线程）
void onSensorData(const SensorData& data) {
    queue_.push(data);  // 无锁，O(1)
}

// 消费者（处理线程）
void processingLoop() {
    SensorData data;
    while (running_) {
        if (queue_.pop(data)) {
            process(data);
        }
    }
}
```

## 审查要点

- [ ] 共享变量是否使用 `std::atomic` 或互斥锁保护
- [ ] 锁的粒度是否最小化（尽量缩小临界区）
- [ ] 是否存在死锁风险（循环依赖、嵌套锁）
- [ ] 条件变量是否使用 `while` 而非 `if`（防止虚假唤醒）
- [ ] 线程销毁前是否安全停止（信号量/join/atomic flag）
- [ ] 实时线程是否使用了非实时锁
