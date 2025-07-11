# SM3基础版本 Makefile

CXX = g++
CXXFLAGS = -std=c++11 -O3 -Wall -Wextra -march=native
TARGET = sm3_basic
SOURCES = sm3.cpp main.cpp
HEADERS = sm3.h
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

# 运行测试
test: $(TARGET)
	./$(TARGET)

# 清理
clean:
	rm -f $(OBJECTS) $(TARGET) *.exe

# 安装（可选）
install: $(TARGET)
	cp $(TARGET) /usr/local/bin/

# 显示编译信息
info:
	@echo "编译器: $(CXX)"
	@echo "编译选项: $(CXXFLAGS)"
	@echo "源文件: $(SOURCES)"
	@echo "目标文件: $(TARGET)"

# 帮助
help:
	@echo "可用的make目标:"
	@echo "  all      - 编译基础版本(默认)"
	@echo "  debug    - 编译调试版本"
	@echo "  profile  - 编译性能分析版本"
	@echo "  test     - 编译并运行测试"
	@echo "  clean    - 清理编译文件"
	@echo "  install  - 安装到系统"
	@echo "  info     - 显示编译信息"
	@echo "  help     - 显示此帮助"

.PHONY: all debug profile test clean install info help 