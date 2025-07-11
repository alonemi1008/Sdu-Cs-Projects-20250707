# SM3 SIMD版本 Makefile

CXX = g++
CXXFLAGS = -std=c++11 -O3 -Wall -Wextra -march=native -mavx2 -msse4.2
TARGET = sm3_simd
SOURCES = sm3_simd.cpp main_simd.cpp
HEADERS = sm3_simd.h
OBJECTS = $(SOURCES:.cpp=.o)

# 默认目标
all: $(TARGET)

# 编译主程序
$(TARGET): $(OBJECTS)
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(OBJECTS)

# 编译对象文件
%.o: %.cpp $(HEADERS)
	$(CXX) $(CXXFLAGS) -c $< -o $@

# 调试版本
debug: CXXFLAGS += -g -DDEBUG -O0
debug: $(TARGET)

# 性能分析版本
profile: CXXFLAGS += -pg -O2
profile: $(TARGET)

# 汇编输出版本（用于分析SIMD指令生成）
asm: CXXFLAGS += -S -masm=intel
asm: $(SOURCES:.cpp=.s)

%.s: %.cpp $(HEADERS)
	$(CXX) $(CXXFLAGS) -c $< -o $@

# 运行测试
test: $(TARGET)
	./$(TARGET)

# 清理
clean:
	rm -f $(OBJECTS) $(TARGET) *.exe *.s

# 安装（可选）
install: $(TARGET)
	cp $(TARGET) /usr/local/bin/

# 显示编译信息
info:
	@echo "编译器: $(CXX)"
	@echo "编译选项: $(CXXFLAGS)"
	@echo "源文件: $(SOURCES)"
	@echo "目标文件: $(TARGET)"
	@echo "SIMD支持: AVX2, SSE4.2"

# CPU特性检测
cpuinfo:
	@echo "CPU信息:"
	@cat /proc/cpuinfo | grep -E "model name|flags" | head -2
	@echo ""
	@echo "SIMD指令集支持检测:"
	@echo "SSE2: " $$(cat /proc/cpuinfo | grep -c sse2)
	@echo "SSE4.2: " $$(cat /proc/cpuinfo | grep -c sse4_2)
	@echo "AVX: " $$(cat /proc/cpuinfo | grep -c avx)
	@echo "AVX2: " $$(cat /proc/cpuinfo | grep -c avx2)

# 帮助
help:
	@echo "可用的make目标:"
	@echo "  all      - 编译SIMD版本(默认)"
	@echo "  debug    - 编译调试版本"
	@echo "  profile  - 编译性能分析版本"
	@echo "  asm      - 生成汇编代码"
	@echo "  test     - 编译并运行测试"
	@echo "  clean    - 清理编译文件"
	@echo "  install  - 安装到系统"
	@echo "  info     - 显示编译信息"
	@echo "  cpuinfo  - 显示CPU和SIMD支持信息"
	@echo "  help     - 显示此帮助"

.PHONY: all debug profile asm test clean install info cpuinfo help 