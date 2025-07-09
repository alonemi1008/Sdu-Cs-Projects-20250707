#ifndef _MYTIMER_H_
#define _MYTIMER_H_

#include <iostream>
#include <string>
#include <chrono>
#include <iomanip>
#include <sstream>

/**
 * 高精度计时器类
 * 支持纳秒级别的时间测量
 */
class mytimer {
private:
    // 使用高分辨率时钟
    std::chrono::high_resolution_clock::time_point start_time;
    std::chrono::high_resolution_clock::time_point end_time;
    bool is_running;

public:
    // 构造函数
    mytimer() : is_running(false) {
        UpDate();
    }

    // 更新时间点（开始或结束）
    void UpDate() {
        if (is_running) {
            end_time = std::chrono::high_resolution_clock::now();
        } else {
            start_time = std::chrono::high_resolution_clock::now();
            is_running = true;
        }
    }

    // 重置计时器
    void Reset() {
        start_time = std::chrono::high_resolution_clock::now();
        is_running = true;
    }

    // 获取经过的秒数
    double GetSecond() {
        if (!is_running) {
            return 0.0;
        }
        auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>(end_time - start_time);
        return duration.count() / 1000000000.0;
    }

    // 获取经过的毫秒数
    double GetMillisecond() {
        if (!is_running) {
            return 0.0;
        }
        auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>(end_time - start_time);
        return duration.count() / 1000000.0;
    }

    // 获取经过的微秒数
    double GetMicrosecond() {
        if (!is_running) {
            return 0.0;
        }
        auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>(end_time - start_time);
        return duration.count() / 1000.0;
    }

    // 获取经过的纳秒数
    double GetNanosecond() {
        if (!is_running) {
            return 0.0;
        }
        auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>(end_time - start_time);
        return static_cast<double>(duration.count());
    }

    // 获取格式化的时间字符串
    std::string GetFormattedTime(int precision = 9) {
        double seconds = GetSecond();
        std::stringstream ss;
        ss << std::fixed << std::setprecision(precision) << seconds << " s";
        
        // 添加其他单位的表示
        if (seconds < 0.000001) {
            double ns = GetNanosecond();
            ss << " (" << std::fixed << std::setprecision(3) << ns << " ns)";
        } else if (seconds < 0.001) {
            double us = GetMicrosecond();
            ss << " (" << std::fixed << std::setprecision(3) << us << " μs)";
        } else if (seconds < 1.0) {
            double ms = GetMillisecond();
            ss << " (" << std::fixed << std::setprecision(3) << ms << " ms)";
        }
        
        return ss.str();
    }
    
    // 获取不同精度的格式化时间
    std::string GetDetailedTime() {
        std::stringstream ss;
        ss << std::fixed << std::setprecision(9) << GetSecond() << " s, "
           << std::fixed << std::setprecision(6) << GetMillisecond() << " ms, "
           << std::fixed << std::setprecision(3) << GetMicrosecond() << " μs, "
           << std::fixed << std::setprecision(0) << GetNanosecond() << " ns";
        return ss.str();
    }
};

#endif