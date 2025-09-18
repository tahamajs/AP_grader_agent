#ifndef EVENT_MANAGER_H
#define EVENT_MANAGER_H

#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
#include <sstream>
#include <stdexcept>
#include <regex>
#include <chrono>
#include <thread>
#include <atomic>
#include <mutex>

// ====================
// CONSTANTS & CONFIG
// ====================
const std::string TIME_FORMAT_REGEX = "^([01]?[0-9]|2[0-3]):[0-5][0-9]$";
const int MAX_EVENT_NAME_LENGTH = 50;
const int MIN_EVENT_DURATION_MINUTES = 15;
const int MAX_PERIODIC_EVENTS = 100;

// ====================
// EXCEPTION CLASSES
// ====================
class EventException : public std::runtime_error {
public:
    explicit EventException(const std::string& message) : std::runtime_error(message) {}
};

class TimeConflictException : public EventException {
public:
    explicit TimeConflictException(const std::string& message) : EventException(message) {}
};

class InvalidTimeFormatException : public EventException {
public:
    explicit InvalidTimeFormatException(const std::string& message) : EventException(message) {}
};

class TaskException : public EventException {
public:
    explicit TaskException(const std::string& message) : EventException(message) {}
};

// ====================
// DATA STRUCTURES
// ====================
struct TimeSlot {
    int hours;
    int minutes;

    TimeSlot(int h = 0, int m = 0) : hours(h), minutes(m) {}

    int toMinutes() const {
        return hours * 60 + minutes;
    }

    std::string toString() const {
        char buffer[6];
        snprintf(buffer, sizeof(buffer), "%02d:%02d", hours, minutes);
        return std::string(buffer);
    }

    static TimeSlot fromString(const std::string& time_str) {
        if (!std::regex_match(time_str, std::regex(TIME_FORMAT_REGEX))) {
            throw InvalidTimeFormatException("Invalid time format: " + time_str + ". Use HH:MM format.");
        }

        int hours, minutes;
        if (sscanf(time_str.c_str(), "%d:%d", &hours, &minutes) != 2) {
            throw InvalidTimeFormatException("Failed to parse time: " + time_str);
        }

        if (hours < 0 || hours > 23 || minutes < 0 || minutes > 59) {
            throw InvalidTimeFormatException("Time values out of range: " + time_str);
        }

        return TimeSlot(hours, minutes);
    }

    // Comparison operators for sorting
    bool operator<(const TimeSlot& other) const {
        return toMinutes() < other.toMinutes();
    }

    bool operator==(const TimeSlot& other) const {
        return hours == other.hours && minutes == other.minutes;
    }
};

enum class EventType {
    ONE_TIME,
    DAILY,
    WEEKLY,
    MONTHLY
};

enum class TaskStatus {
    PENDING,
    IN_PROGRESS,
    COMPLETED,
    CANCELLED
};

enum class TaskPriority {
    LOW,
    MEDIUM,
    HIGH,
    URGENT
};

struct Event {
    std::string name;
    TimeSlot start_time;
    TimeSlot end_time;
    std::string description;
    EventType type;
    int recurrence_id; // For periodic events, groups related instances

    Event(const std::string& n, const TimeSlot& start, const TimeSlot& end,
          const std::string& desc = "", EventType t = EventType::ONE_TIME, int rec_id = -1)
        : name(n), start_time(start), end_time(end), description(desc), type(t), recurrence_id(rec_id) {}

    int getDurationMinutes() const {
        return end_time.toMinutes() - start_time.toMinutes();
    }

    bool isValid() const {
        return !name.empty() &&
               name.length() <= MAX_EVENT_NAME_LENGTH &&
               start_time.toMinutes() < end_time.toMinutes() &&
               getDurationMinutes() >= MIN_EVENT_DURATION_MINUTES;
    }

    std::string getTypeString() const {
        switch (type) {
            case EventType::ONE_TIME: return "One-time";
            case EventType::DAILY: return "Daily";
            case EventType::WEEKLY: return "Weekly";
            case EventType::MONTHLY: return "Monthly";
            default: return "Unknown";
        }
    }
};

struct Task {
    std::string title;
    std::string description;
    TaskStatus status;
    TaskPriority priority;
    TimeSlot deadline;
    std::string assigned_to;
    int task_id;

    Task(const std::string& t, const std::string& desc, TaskPriority p = TaskPriority::MEDIUM,
         const TimeSlot& dl = TimeSlot(), const std::string& assignee = "", int id = -1)
        : title(t), description(desc), status(TaskStatus::PENDING), priority(p),
          deadline(dl), assigned_to(assignee), task_id(id) {}

    std::string getStatusString() const {
        switch (status) {
            case TaskStatus::PENDING: return "Pending";
            case TaskStatus::IN_PROGRESS: return "In Progress";
            case TaskStatus::COMPLETED: return "Completed";
            case TaskStatus::CANCELLED: return "Cancelled";
            default: return "Unknown";
        }
    }

    std::string getPriorityString() const {
        switch (priority) {
            case TaskPriority::LOW: return "Low";
            case TaskPriority::MEDIUM: return "Medium";
            case TaskPriority::HIGH: return "High";
            case TaskPriority::URGENT: return "Urgent";
            default: return "Unknown";
        }
    }

    bool isOverdue() const {
        if (status == TaskStatus::COMPLETED || status == TaskStatus::CANCELLED) {
            return false;
        }
        // For simplicity, assume current time is 12:00 for overdue check
        TimeSlot current_time(12, 0);
        return deadline.toMinutes() < current_time.toMinutes();
    }
};

struct User {
    std::string username;
    std::string password; // In real app, this would be hashed
    std::vector<std::string> event_permissions;
    std::vector<std::string> task_permissions;

    User(const std::string& user, const std::string& pass)
        : username(user), password(pass) {}
};

// ====================
// EVENT MANAGER CLASS
// ====================
class EventManager {
private:
    std::vector<Event> events;
    std::vector<Task> tasks;
    std::vector<User> users;
    User* current_user;
    mutable std::mutex data_mutex;
    std::atomic<bool> running;
    int next_task_id;
    int next_recurrence_id;

    // Check if two time ranges overlap
    bool hasTimeConflict(const Event& new_event) const {
        int new_start = new_event.start_time.toMinutes();
        int new_end = new_event.end_time.toMinutes();

        for (const auto& existing : events) {
            // Skip if same recurrence group (for periodic events)
            if (new_event.recurrence_id != -1 && existing.recurrence_id == new_event.recurrence_id) {
                continue;
            }

            int existing_start = existing.start_time.toMinutes();
            int existing_end = existing.end_time.toMinutes();

            // Check for overlap: new event starts before existing ends AND new event ends after existing starts
            if (new_start < existing_end && new_end > existing_start) {
                return true;
            }
        }
        return false;
    }

    // Sort events by start time
    static bool compareByStartTime(const Event& a, const Event& b) {
        return a.start_time.toMinutes() < b.start_time.toMinutes();
    }

    // Sort tasks by priority and deadline
    static bool compareByPriorityAndDeadline(const Task& a, const Task& b) {
        if (a.priority != b.priority) {
            return static_cast<int>(a.priority) > static_cast<int>(b.priority);
        }
        return a.deadline.toMinutes() < b.deadline.toMinutes();
    }

    // Validate event name
    bool isValidEventName(const std::string& name) const {
        if (name.empty() || name.length() > MAX_EVENT_NAME_LENGTH) {
            return false;
        }

        // Check for duplicate names (only for one-time events)
        return std::find_if(events.begin(), events.end(),
            [&name](const Event& e) { return e.name == name && e.type == EventType::ONE_TIME; }) == events.end();
    }

    // Generate periodic event instances
    void generatePeriodicEvents(const Event& base_event, int count = 7) {
        if (base_event.type == EventType::ONE_TIME || count <= 0) {
            return;
        }

        int recurrence_id = next_recurrence_id++;
        events.push_back(Event(base_event.name, base_event.start_time, base_event.end_time,
                              base_event.description, base_event.type, recurrence_id));

        TimeSlot current_start = base_event.start_time;
        TimeSlot current_end = base_event.end_time;

        for (int i = 1; i < count && events.size() < MAX_PERIODIC_EVENTS; ++i) {
            switch (base_event.type) {
                case EventType::DAILY:
                    current_start.hours = (current_start.hours + 24) % 24;
                    current_end.hours = (current_end.hours + 24) % 24;
                    break;
                case EventType::WEEKLY:
                    current_start.hours = (current_start.hours + 24 * 7) % 24;
                    current_end.hours = (current_end.hours + 24 * 7) % 24;
                    break;
                case EventType::MONTHLY:
                    // Simple monthly approximation (30 days)
                    current_start.hours = (current_start.hours + 24 * 30) % 24;
                    current_end.hours = (current_end.hours + 24 * 30) % 24;
                    break;
                default:
                    return;
            }

            std::string instance_name = base_event.name + " #" + std::to_string(i + 1);
            Event instance(instance_name, current_start, current_end,
                          base_event.description, base_event.type, recurrence_id);

            if (!hasTimeConflict(instance)) {
                events.push_back(instance);
            }
        }
    }

public:
    EventManager() : current_user(nullptr), running(false), next_task_id(1), next_recurrence_id(1) {}

    ~EventManager() {
        stopPeriodicUpdates();
    }

    // ====================
    // AUTHENTICATION METHODS
    // ====================
    void login(const std::string& username, const std::string& password) {
        std::lock_guard<std::mutex> lock(data_mutex);
        auto it = std::find_if(users.begin(), users.end(),
            [&username](const User& u) { return u.username == username; });

        if (it != users.end() && it->password == password) {
            current_user = &(*it);
            std::cout << "Login successful. Welcome, " << username << "!" << std::endl;
            return;
        }

        throw EventException("Invalid username or password.");
    }

    void signup(const std::string& username, const std::string& password) {
        std::lock_guard<std::mutex> lock(data_mutex);

        // Validate input
        if (username.empty() || password.empty()) {
            throw EventException("Username and password cannot be empty.");
        }

        if (username.length() < 3 || password.length() < 6) {
            throw EventException("Username must be at least 3 characters, password at least 6 characters.");
        }

        // Check if user already exists
        auto it = std::find_if(users.begin(), users.end(),
            [&username](const User& u) { return u.username == username; });

        if (it != users.end()) {
            throw EventException("Username already exists. Please choose a different username.");
        }

        users.emplace_back(username, password);
        std::cout << "Account created successfully. You can now login." << std::endl;
    }

    void logout() {
        std::lock_guard<std::mutex> lock(data_mutex);
        if (current_user) {
            std::cout << "Logged out successfully. Goodbye, " << current_user->username << "!" << std::endl;
            current_user = nullptr;
            return;
        }
        throw EventException("No user is currently logged in.");
    }

    bool isLoggedIn() const {
        return current_user != nullptr;
    }

    // ====================
    // EVENT MANAGEMENT METHODS
    // ====================
    void addEvent(const std::string& name, const std::string& start_time_str,
                  const std::string& end_time_str, const std::string& description = "",
                  EventType type = EventType::ONE_TIME) {
        std::lock_guard<std::mutex> lock(data_mutex);

        if (!isLoggedIn()) {
            throw EventException("You must be logged in to add events.");
        }

        if (!isValidEventName(name)) {
            throw EventException("Invalid event name: " + name + ". Name must be unique and 1-50 characters.");
        }

        TimeSlot start_time = TimeSlot::fromString(start_time_str);
        TimeSlot end_time = TimeSlot::fromString(end_time_str);

        Event new_event(name, start_time, end_time, description, type);

        if (!new_event.isValid()) {
            throw EventException("Invalid event: duration must be at least 15 minutes.");
        }

        if (hasTimeConflict(new_event)) {
            throw TimeConflictException("Time conflict detected with existing event.");
        }

        if (type == EventType::ONE_TIME) {
            events.push_back(new_event);
            std::cout << "Event '" << name << "' added successfully from "
                      << start_time.toString() << " to " << end_time.toString() << "." << std::endl;
        } else {
            generatePeriodicEvents(new_event);
            std::cout << "Periodic event '" << name << "' (" << new_event.getTypeString()
                      << ") added successfully." << std::endl;
        }
    }

    void removeEvent(const std::string& name) {
        std::lock_guard<std::mutex> lock(data_mutex);

        if (!isLoggedIn()) {
            throw EventException("You must be logged in to remove events.");
        }

        auto it = std::find_if(events.begin(), events.end(),
            [&name](const Event& e) { return e.name == name; });

        if (it == events.end()) {
            throw EventException("Event '" + name + "' not found.");
        }

        // If it's a periodic event, remove all instances with same recurrence_id
        if (it->type != EventType::ONE_TIME && it->recurrence_id != -1) {
            int recurrence_id = it->recurrence_id;
            events.erase(std::remove_if(events.begin(), events.end(),
                [recurrence_id](const Event& e) { return e.recurrence_id == recurrence_id; }), events.end());
            std::cout << "Periodic event series removed successfully." << std::endl;
        } else {
            events.erase(it);
            std::cout << "Event '" << name << "' removed successfully." << std::endl;
        }
    }

    void listEvents() const {
        std::lock_guard<std::mutex> lock(data_mutex);

        if (!isLoggedIn()) {
            throw EventException("You must be logged in to view events.");
        }

        if (events.empty()) {
            std::cout << "No events scheduled." << std::endl;
            return;
        }

        // Create a copy and sort it
        std::vector<Event> sorted_events = events;
        std::sort(sorted_events.begin(), sorted_events.end(), compareByStartTime);

        std::cout << "Scheduled Events (" << sorted_events.size() << " total):" << std::endl;
        std::cout << std::string(60, '=') << std::endl;

        for (size_t i = 0; i < sorted_events.size(); ++i) {
            const auto& event = sorted_events[i];
            std::cout << (i + 1) << ". " << event.name;
            if (event.type != EventType::ONE_TIME) {
                std::cout << " [" << event.getTypeString() << "]";
            }
            std::cout << std::endl;
            std::cout << "   Time: " << event.start_time.toString() << " - " << event.end_time.toString()
                      << " (" << event.getDurationMinutes() << " minutes)" << std::endl;
            if (!event.description.empty()) {
                std::cout << "   Description: " << event.description << std::endl;
            }
            std::cout << std::endl;
        }
    }

    // ====================
    // TASK MANAGEMENT METHODS
    // ====================
    void addTask(const std::string& title, const std::string& description = "",
                 TaskPriority priority = TaskPriority::MEDIUM, const std::string& deadline_str = "",
                 const std::string& assignee = "") {
        std::lock_guard<std::mutex> lock(data_mutex);

        if (!isLoggedIn()) {
            throw TaskException("You must be logged in to add tasks.");
        }

        if (title.empty()) {
            throw TaskException("Task title cannot be empty.");
        }

        TimeSlot deadline;
        if (!deadline_str.empty()) {
            deadline = TimeSlot::fromString(deadline_str);
        }

        std::string actual_assignee = assignee.empty() ? current_user->username : assignee;

        Task new_task(title, description, priority, deadline, actual_assignee, next_task_id++);
        tasks.push_back(new_task);

        std::cout << "Task '" << title << "' added successfully (ID: " << new_task.task_id
                  << ", Priority: " << new_task.getPriorityString() << ")." << std::endl;
    }

    void updateTaskStatus(int task_id, TaskStatus status) {
        std::lock_guard<std::mutex> lock(data_mutex);

        if (!isLoggedIn()) {
            throw TaskException("You must be logged in to update tasks.");
        }

        auto it = std::find_if(tasks.begin(), tasks.end(),
            [task_id](const Task& t) { return t.task_id == task_id; });

        if (it == tasks.end()) {
            throw TaskException("Task with ID " + std::to_string(task_id) + " not found.");
        }

        // Check permissions
        if (it->assigned_to != current_user->username && !hasTaskPermission("admin")) {
            throw TaskException("You don't have permission to update this task.");
        }

        it->status = status;
        std::cout << "Task '" << it->title << "' status updated to " << it->getStatusString() << "." << std::endl;
    }

    void removeTask(int task_id) {
        std::lock_guard<std::mutex> lock(data_mutex);

        if (!isLoggedIn()) {
            throw TaskException("You must be logged in to remove tasks.");
        }

        auto it = std::find_if(tasks.begin(), tasks.end(),
            [task_id](const Task& t) { return t.task_id == task_id; });

        if (it == tasks.end()) {
            throw TaskException("Task with ID " + std::to_string(task_id) + " not found.");
        }

        // Check permissions
        if (it->assigned_to != current_user->username && !hasTaskPermission("admin")) {
            throw TaskException("You don't have permission to remove this task.");
        }

        std::string title = it->title;
        tasks.erase(it);
        std::cout << "Task '" << title << "' removed successfully." << std::endl;
    }

    void listTasks() const {
        std::lock_guard<std::mutex> lock(data_mutex);

        if (!isLoggedIn()) {
            throw TaskException("You must be logged in to view tasks.");
        }

        if (tasks.empty()) {
            std::cout << "No tasks available." << std::endl;
            return;
        }

        // Create a copy and sort it
        std::vector<Task> sorted_tasks = tasks;
        std::sort(sorted_tasks.begin(), sorted_tasks.end(), compareByPriorityAndDeadline);

        std::cout << "Tasks (" << sorted_tasks.size() << " total):" << std::endl;
        std::cout << std::string(80, '=') << std::endl;

        for (const auto& task : sorted_tasks) {
            std::cout << "ID: " << task.task_id << " | " << task.title << std::endl;
            std::cout << "   Status: " << task.getStatusString()
                      << " | Priority: " << task.getPriorityString() << std::endl;
            std::cout << "   Assigned to: " << task.assigned_to << std::endl;
            if (task.deadline.toMinutes() > 0) {
                std::cout << "   Deadline: " << task.deadline.toString();
                if (task.isOverdue()) {
                    std::cout << " (OVERDUE)";
                }
                std::cout << std::endl;
            }
            if (!task.description.empty()) {
                std::cout << "   Description: " << task.description << std::endl;
            }
            std::cout << std::endl;
        }
    }

    // ====================
    // PERIODIC UPDATES
    // ====================
    void startPeriodicUpdates() {
        if (running) {
            std::cout << "Periodic updates already running." << std::endl;
            return;
        }

        running = true;
        std::thread([this]() {
            while (running) {
                std::this_thread::sleep_for(std::chrono::minutes(60)); // Update every hour
                performPeriodicUpdates();
            }
        }).detach();

        std::cout << "Periodic updates started." << std::endl;
    }

    void stopPeriodicUpdates() {
        running = false;
        std::cout << "Periodic updates stopped." << std::endl;
    }

    void performPeriodicUpdates() {
        std::lock_guard<std::mutex> lock(data_mutex);

        // Refresh periodic events
        std::vector<Event> periodic_events;
        for (const auto& event : events) {
            if (event.type != EventType::ONE_TIME) {
                periodic_events.push_back(event);
            }
        }

        // Regenerate upcoming instances for periodic events
        for (const auto& base_event : periodic_events) {
            if (events.size() < MAX_PERIODIC_EVENTS) {
                generatePeriodicEvents(base_event, 1); // Add one more instance
            }
        }

        // Check for overdue tasks
        for (auto& task : tasks) {
            if (task.isOverdue() && task.status != TaskStatus::COMPLETED) {
                std::cout << "ALERT: Task '" << task.title << "' is overdue!" << std::endl;
            }
        }
    }

    // ====================
    // UTILITY METHODS
    // ====================
    size_t getEventCount() const {
        std::lock_guard<std::mutex> lock(data_mutex);
        return events.size();
    }

    size_t getTaskCount() const {
        std::lock_guard<std::mutex> lock(data_mutex);
        return tasks.size();
    }

    void clearAllEvents() {
        std::lock_guard<std::mutex> lock(data_mutex);
        if (!isLoggedIn()) {
            throw EventException("You must be logged in to clear events.");
        }
        events.clear();
        std::cout << "All events cleared." << std::endl;
    }

    void clearAllTasks() {
        std::lock_guard<std::mutex> lock(data_mutex);
        if (!isLoggedIn()) {
            throw TaskException("You must be logged in to clear tasks.");
        }
        tasks.clear();
        std::cout << "All tasks cleared." << std::endl;
    }

private:
    bool hasTaskPermission(const std::string& permission) const {
        if (!current_user) return false;
        return std::find(current_user->task_permissions.begin(),
                        current_user->task_permissions.end(), permission) != current_user->task_permissions.end();
    }
};

#endif // EVENT_MANAGER_H