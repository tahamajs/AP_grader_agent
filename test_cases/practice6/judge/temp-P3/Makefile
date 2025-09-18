# Event Management System Makefile
# This Makefile provides targets for building, cleaning, and testing the project

# Compiler and flags
CXX = g++
CXXFLAGS = -std=c++17 -Wall -Wextra -Werror -pedantic -O2
LDFLAGS =

# Source files
SOURCES = main.cpp
HEADERS = EventManager.h
TEST_SOURCES = test_suite.cpp
TEST_EXECUTABLE = test_suite

# Object files
OBJECTS = $(SOURCES:.cpp=.o)
TEST_OBJECTS = $(TEST_SOURCES:.cpp=.o)

# Executable name
EXECUTABLE = event_manager

# Default target
all: $(EXECUTABLE)

# Link object files to create executable
$(EXECUTABLE): $(OBJECTS)
	$(CXX) $(LDFLAGS) $(OBJECTS) -o $(EXECUTABLE)
	@echo "Build successful! Run './$(EXECUTABLE)' to start the program."

# Compile source files to object files
%.o: %.cpp $(HEADERS)
	$(CXX) $(CXXFLAGS) -c $< -o $@

# Compile test files
test_%.o: test_%.cpp $(HEADERS)
	$(CXX) $(CXXFLAGS) -c $< -o $@

# Clean build artifacts
clean:
	rm -f $(OBJECTS) $(EXECUTABLE)
	@echo "Cleaned build artifacts."

# Clean and rebuild
rebuild: clean all

# Run the program
run: $(EXECUTABLE)
	./$(EXECUTABLE)

# Debug build with symbols
debug: CXXFLAGS += -g -DDEBUG
debug: clean all

# Test compilation without linking
syntax-check:
	$(CXX) $(CXXFLAGS) -fsyntax-only $(SOURCES)

# Show help
help:
	@echo "Available targets:"
	@echo "  all          - Build the executable (default)"
	@echo "  clean        - Remove build artifacts"
	@echo "  rebuild      - Clean and rebuild"
	@echo "  run          - Build and run the program"
	@echo "  debug        - Build with debug symbols"
	@echo "  syntax-check - Check syntax without compiling"
	@echo "  test         - Build and run test suite"
	@echo "  test-build   - Build test suite only"
	@echo "  help         - Show this help message"

# Build test suite
test-build: $(TEST_OBJECTS) $(filter-out main.o, $(OBJECTS))
	$(CXX) $(LDFLAGS) $(TEST_OBJECTS) $(filter-out main.o, $(OBJECTS)) -o $(TEST_EXECUTABLE)
	@echo "Test suite built successfully."

# Run test suite
test: test-build
	./$(TEST_EXECUTABLE)

.PHONY: all clean rebuild run debug syntax-check help test test-build