#include "EventManager.h"
#include <iostream>
#include <cassert>
#include <vector>
#include <string>

// ====================
// TEST HELPER FUNCTIONS
// ====================
void printTestResult(const std::string& testName, bool passed) {
    std::cout << "[" << (passed ? "PASS" : "FAIL") << "] " << testName << std::endl;
}

void printTestHeader(const std::string& header) {
    std::cout << "\n" << std::string(50, '=') << std::endl;
    std::cout << "TESTING: " << header << std::endl;
    std::cout << std::string(50, '=') << std::endl;
}

// ====================
// AUTHENTICATION TESTS
// ====================
void testAuthentication() {
    printTestHeader("Authentication System");

    EventManager manager;

    // Test signup
    bool signup1 = false, signup2 = false, signup3 = false;
    try {
        manager.signup("testuser", "password123");
        signup1 = true;
    } catch (const std::exception&) {}

    try {
        manager.signup("testuser", "password123"); // Should fail - duplicate
        signup2 = false;
    } catch (const std::exception&) {
        signup2 = true; // Expected to fail
    }

    try {
        manager.signup("", "password123"); // Should fail - empty username
        signup3 = false;
    } catch (const std::exception&) {
        signup3 = true; // Expected to fail
    }

    printTestResult("Signup valid user", signup1);
    printTestResult("Signup duplicate user", signup2);
    printTestResult("Signup empty username", signup3);

    // Test login
    bool login1 = false, login2 = false, login3 = false;
    try {
        manager.login("testuser", "password123");
        login1 = true;
    } catch (const std::exception&) {}

    try {
        manager.login("testuser", "wrongpassword"); // Should fail
        login2 = false;
    } catch (const std::exception&) {
        login2 = true; // Expected to fail
    }

    try {
        manager.login("nonexistent", "password123"); // Should fail
        login3 = false;
    } catch (const std::exception&) {
        login3 = true; // Expected to fail
    }

    printTestResult("Login valid credentials", login1);
    printTestResult("Login wrong password", login2);
    printTestResult("Login nonexistent user", login3);

    // Test logout
    bool logout1 = false;
    try {
        manager.logout();
        logout1 = true;
    } catch (const std::exception&) {}

    printTestResult("Logout when logged in", logout1);
}

// ====================
// EVENT MANAGEMENT TESTS
// ====================
void testEventManagement() {
    printTestHeader("Event Management");

    EventManager manager;

    // Setup: signup and login
    try {
        manager.signup("testuser", "password123");
        manager.login("testuser", "password123");
    } catch (const std::exception& e) {
        std::cout << "Setup failed: " << e.what() << std::endl;
        return;
    }

    // Test adding events
    bool addEvent1 = false, addEvent2 = false, addEvent3 = false;
    try {
        manager.addEvent("Meeting", "09:00", "10:00", "Team meeting");
        addEvent1 = true;
    } catch (const std::exception&) {}

    try {
        manager.addEvent("Lunch", "12:00", "12:30", "Lunch break");
        addEvent2 = true;
    } catch (const std::exception&) {}

    try {
        manager.addEvent("Meeting", "09:00", "10:00", "Duplicate name"); // Should fail
        addEvent3 = false;
    } catch (const std::exception&) {
        addEvent3 = true; // Expected to fail
    }

    printTestResult("Add valid event", addEvent1);
    printTestResult("Add second valid event", addEvent2);
    printTestResult("Add duplicate event name", addEvent3);

    // Test time conflict
    bool timeConflict = false;
    try {
        manager.addEvent("Conflict", "09:30", "10:30", "Should conflict"); // Should fail
        timeConflict = false;
    } catch (const std::exception&) {
        timeConflict = true; // Expected to fail
    }

    printTestResult("Detect time conflict", timeConflict);

    // Test invalid time format
    bool invalidTime = false;
    try {
        manager.addEvent("Invalid", "25:00", "26:00", "Invalid time"); // Should fail
        invalidTime = false;
    } catch (const std::exception&) {
        invalidTime = true; // Expected to fail
    }

    printTestResult("Detect invalid time format", invalidTime);

    // Test event count
    bool eventCount = (manager.getEventCount() == 2);
    printTestResult("Correct event count", eventCount);

    // Test removing events
    bool removeEvent1 = false, removeEvent2 = false;
    try {
        manager.removeEvent("Meeting");
        removeEvent1 = true;
    } catch (const std::exception&) {}

    try {
        manager.removeEvent("NonExistent"); // Should fail
        removeEvent2 = false;
    } catch (const std::exception&) {
        removeEvent2 = true; // Expected to fail
    }

    printTestResult("Remove existing event", removeEvent1);
    printTestResult("Remove nonexistent event", removeEvent2);
}

// ====================
// PERIODIC EVENT TESTS
// ====================
void testPeriodicEvents() {
    printTestHeader("Periodic Events");

    EventManager manager;

    // Setup: signup and login
    try {
        manager.signup("testuser", "password123");
        manager.login("testuser", "password123");
    } catch (const std::exception& e) {
        std::cout << "Setup failed: " << e.what() << std::endl;
        return;
    }

    // Test adding periodic events
    bool addDaily = false, addWeekly = false, addMonthly = false;
    try {
        manager.addEvent("Daily Standup", "09:00", "09:15", "Daily meeting", EventType::DAILY);
        addDaily = true;
    } catch (const std::exception&) {}

    try {
        manager.addEvent("Weekly Review", "14:00", "15:00", "Weekly review", EventType::WEEKLY);
        addWeekly = true;
    } catch (const std::exception&) {}

    try {
        manager.addEvent("Monthly Report", "10:00", "11:00", "Monthly report", EventType::MONTHLY);
        addMonthly = true;
    } catch (const std::exception&) {}

    printTestResult("Add daily periodic event", addDaily);
    printTestResult("Add weekly periodic event", addWeekly);
    printTestResult("Add monthly periodic event", addMonthly);

    // Check that periodic events generate multiple instances
    bool hasMultipleInstances = (manager.getEventCount() >= 3);
    printTestResult("Periodic events generate multiple instances", hasMultipleInstances);
}

// ====================
// TASK MANAGEMENT TESTS
// ====================
void testTaskManagement() {
    printTestHeader("Task Management");

    EventManager manager;

    // Setup: signup and login
    try {
        manager.signup("testuser", "password123");
        manager.login("testuser", "password123");
    } catch (const std::exception& e) {
        std::cout << "Setup failed: " << e.what() << std::endl;
        return;
    }

    // Test adding tasks
    bool addTask1 = false, addTask2 = false;
    try {
        manager.addTask("Write documentation", "Write API documentation", TaskPriority::HIGH, "17:00");
        addTask1 = true;
    } catch (const std::exception&) {}

    try {
        manager.addTask("Code review", "Review pull requests", TaskPriority::MEDIUM);
        addTask2 = true;
    } catch (const std::exception&) {}

    printTestResult("Add task with deadline", addTask1);
    printTestResult("Add task without deadline", addTask2);

    // Test task count
    bool taskCount = (manager.getTaskCount() == 2);
    printTestResult("Correct task count", taskCount);

    // Test updating task status
    bool updateStatus = false;
    try {
        manager.updateTaskStatus(1, TaskStatus::COMPLETED);
        updateStatus = true;
    } catch (const std::exception&) {}

    printTestResult("Update task status", updateStatus);

    // Test removing tasks
    bool removeTask1 = false, removeTask2 = false;
    try {
        manager.removeTask(1);
        removeTask1 = true;
    } catch (const std::exception&) {}

    try {
        manager.removeTask(999); // Should fail
        removeTask2 = false;
    } catch (const std::exception&) {
        removeTask2 = true; // Expected to fail
    }

    printTestResult("Remove existing task", removeTask1);
    printTestResult("Remove nonexistent task", removeTask2);
}

// ====================
// EXCEPTION HANDLING TESTS
// ====================
void testExceptionHandling() {
    printTestHeader("Exception Handling");

    EventManager manager;

    // Test operations without login
    bool noLoginEvent = false, noLoginTask = false;
    try {
        manager.addEvent("Test", "10:00", "11:00");
        noLoginEvent = false;
    } catch (const std::exception&) {
        noLoginEvent = true; // Expected to fail
    }

    try {
        manager.addTask("Test Task");
        noLoginTask = false;
    } catch (const std::exception&) {
        noLoginTask = true; // Expected to fail
    }

    printTestResult("Prevent event operations without login", noLoginEvent);
    printTestResult("Prevent task operations without login", noLoginTask);

    // Test invalid time formats
    manager.signup("testuser", "password123");
    manager.login("testuser", "password123");

    bool invalidTime1 = false, invalidTime2 = false, invalidTime3 = false;
    try {
        manager.addEvent("Test", "25:00", "26:00"); // Invalid hours
        invalidTime1 = false;
    } catch (const std::exception&) {
        invalidTime1 = true; // Expected to fail
    }

    try {
        manager.addEvent("Test", "10:60", "11:00"); // Invalid minutes
        invalidTime2 = false;
    } catch (const std::exception&) {
        invalidTime2 = true; // Expected to fail
    }

    try {
        manager.addEvent("Test", "10:00", "09:00"); // End before start
        invalidTime3 = false;
    } catch (const std::exception&) {
        invalidTime3 = true; // Expected to fail
    }

    printTestResult("Detect invalid hours", invalidTime1);
    printTestResult("Detect invalid minutes", invalidTime2);
    printTestResult("Detect end before start", invalidTime3);
}

// ====================
// TIME SLOT TESTS
// ====================
void testTimeSlot() {
    printTestHeader("TimeSlot Functionality");

    // Test valid time parsing
    bool validTime1 = false, validTime2 = false;
    try {
        TimeSlot ts1 = TimeSlot::fromString("09:30");
        validTime1 = (ts1.hours == 9 && ts1.minutes == 30);
    } catch (const std::exception&) {}

    try {
        TimeSlot ts2 = TimeSlot::fromString("23:59");
        validTime2 = (ts2.hours == 23 && ts2.minutes == 59);
    } catch (const std::exception&) {}

    printTestResult("Parse valid time 09:30", validTime1);
    printTestResult("Parse valid time 23:59", validTime2);

    // Test invalid time parsing
    bool invalidTime1 = false, invalidTime2 = false, invalidTime3 = false;
    try {
        TimeSlot::fromString("25:00"); // Invalid hours
        invalidTime1 = false;
    } catch (const std::exception&) {
        invalidTime1 = true; // Expected to fail
    }

    try {
        TimeSlot::fromString("10:60"); // Invalid minutes
        invalidTime2 = false;
    } catch (const std::exception&) {
        invalidTime2 = true; // Expected to fail
    }

    try {
        TimeSlot::fromString("10-30"); // Wrong format
        invalidTime3 = false;
    } catch (const std::exception&) {
        invalidTime3 = true; // Expected to fail
    }

    printTestResult("Reject invalid hours", invalidTime1);
    printTestResult("Reject invalid minutes", invalidTime2);
    printTestResult("Reject wrong format", invalidTime3);

    // Test time conversion
    TimeSlot ts(10, 30);
    bool conversion = (ts.toMinutes() == 630);
    printTestResult("Convert time to minutes", conversion);

    // Test string conversion
    std::string timeStr = ts.toString();
    bool stringConv = (timeStr == "10:30");
    printTestResult("Convert time to string", stringConv);
}

// ====================
// INTEGRATION TESTS
// ====================
void testIntegration() {
    printTestHeader("Integration Tests");

    EventManager manager;

    // Complete workflow test
    bool workflow = false;
    try {
        // 1. Create account and login
        manager.signup("integration", "test123");
        manager.login("integration", "test123");

        // 2. Add various types of events
        manager.addEvent("One-time Meeting", "10:00", "11:00", "Integration test");
        manager.addEvent("Daily Standup", "09:00", "09:15", "", EventType::DAILY);

        // 3. Add tasks
        manager.addTask("Integration Task", "Test integration", TaskPriority::HIGH, "16:00");

        // 4. Update task
        manager.updateTaskStatus(1, TaskStatus::COMPLETED);

        // 5. List everything
        manager.listEvents();
        manager.listTasks();

        // 6. Clean up
        manager.clearAllEvents();
        manager.clearAllTasks();

        workflow = (manager.getEventCount() == 0 && manager.getTaskCount() == 0);
    } catch (const std::exception& e) {
        std::cout << "Integration test failed: " << e.what() << std::endl;
    }

    printTestResult("Complete workflow integration", workflow);
}

// ====================
// MAIN TEST FUNCTION
// ====================
int main() {
    std::cout << "========================================" << std::endl;
    std::cout << "EVENT MANAGEMENT SYSTEM - TEST SUITE" << std::endl;
    std::cout << "========================================" << std::endl;

    // Run all test suites
    testAuthentication();
    testEventManagement();
    testPeriodicEvents();
    testTaskManagement();
    testExceptionHandling();
    testTimeSlot();
    testIntegration();

    std::cout << "\n" << std::string(50, '=') << std::endl;
    std::cout << "TEST SUITE COMPLETED" << std::endl;
    std::cout << std::string(50, '=') << std::endl;

    return 0;
}