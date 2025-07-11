# SM3 性能测试 Makefile

CXX = g++
CXXFLAGS = -std=c++11 -O3 -Wall -Wextra -march=native -mavx2 -msse4.2
TARGET = benchmark
SOURCES = benchmark.cpp ../sm3_basic/sm3.cpp ../sm3_simd/sm3_simd.cpp
HEADERS = ../sm3_basic/sm3.h ../sm3_simd/sm3_simd.h
OBJECTS = $(SOURCES:.cpp=.o)
INCLUDE_DIRS = -I../sm3_basic -I../sm3_simd

# 默认目标
all: $(TARGET)

# 编译主程序
$(TARGET): $(OBJECTS)
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(OBJECTS)

# 编译对象文件
%.o: %.cpp $(HEADERS)
	$(CXX) $(CXXFLAGS) $(INCLUDE_DIRS) -c $< -o $@

# 调试版本
debug: CXXFLAGS += -g -DDEBUG -O0
debug: $(TARGET)

# 性能分析版本
profile: CXXFLAGS += -pg -O2
profile: $(TARGET)

# 运行基准测试
test: $(TARGET)
	./$(TARGET)

# 运行并保存结果
benchmark: $(TARGET)
	./$(TARGET) | tee benchmark_results.txt

# 清理
clean:
	rm -f $(OBJECTS) $(TARGET) *.exe benchmark_results.txt

# 显示编译信息
info:
	@echo "编译器: $(CXX)"
	@echo "编译选项: $(CXXFLAGS)"
	@echo "源文件: $(SOURCES)"
	@echo "目标文件: $(TARGET)"
	@echo "包含目录: $(INCLUDE_DIRS)"

# 帮助
help:
	@echo "可用的make目标:"
	@echo "  all       - 编译基准测试程序(默认)"
	@echo "  debug     - 编译调试版本"
	@echo "  profile   - 编译性能分析版本"
	@echo "  test      - 编译并运行基准测试"
	@echo "  benchmark - 运行基准测试并保存结果"
	@echo "  clean     - 清理编译文件"
	@echo "  info      - 显示编译信息"
	@echo "  help      - 显示此帮助"

.PHONY: all debug profile test benchmark clean info help 