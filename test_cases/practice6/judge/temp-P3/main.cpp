#include "EventManager.h"
#include <iostream>
#include <string>
#include <sstream>

int main() {
    EventManager manager;
    std::string line;

    std::cout << "=== Event Management System ===" << std::endl;
    std::cout << "Available commands:" << std::endl;
    std::cout << "  signup <username> <password>" << std::endl;
    std::cout << "  login <username> <password>" << std::endl;
    std::cout << "  logout" << std::endl;
    std::cout << "  add_event <name> <start_time> <end_time> [description]" << std::endl;
    std::cout << "  add_periodic <name> <start_time> <end_time> <type> [description]" << std::endl;
    std::cout << "  remove_event <name>" << std::endl;
    std::cout << "  list_events" << std::endl;
    std::cout << "  clear_events" << std::endl;
    std::cout << "  add_task <title> [description] [priority] [deadline] [assignee]" << std::endl;
    std::cout << "  update_task <id> <status>" << std::endl;
    std::cout << "  remove_task <id>" << std::endl;
    std::cout << "  list_tasks" << std::endl;
    std::cout << "  clear_tasks" << std::endl;
    std::cout << "  start_updates" << std::endl;
    std::cout << "  stop_updates" << std::endl;
    std::cout << "  help" << std::endl;
    std::cout << "  exit" << std::endl;
    std::cout << std::string(50, '=') << std::endl;

    while (std::getline(std::cin, line)) {
        // Exit on empty line or exit command
        if (line.empty() || line == "exit") {
            break;
        }

        std::istringstream iss(line);
        std::string command;
        iss >> command;

        try {
            if (command == "help") {
                std::cout << "\n=== Available Commands ===" << std::endl;
                std::cout << "Authentication:" << std::endl;
                std::cout << "  signup <username> <password>  - Create new account" << std::endl;
                std::cout << "  login <username> <password>   - Login to account" << std::endl;
                std::cout << "  logout                         - Logout from account" << std::endl;
                std::cout << "\nEvent Management:" << std::endl;
                std::cout << "  add_event <name> <HH:MM> <HH:MM> [desc] - Add one-time event" << std::endl;
                std::cout << "  add_periodic <name> <HH:MM> <HH:MM> <type> [desc] - Add periodic event" << std::endl;
                std::cout << "    Types: daily, weekly, monthly" << std::endl;
                std::cout << "  remove_event <name>            - Remove event" << std::endl;
                std::cout << "  list_events                    - List all events" << std::endl;
                std::cout << "  clear_events                   - Remove all events" << std::endl;
                std::cout << "\nTask Management:" << std::endl;
                std::cout << "  add_task <title> [desc] [priority] [deadline] [assignee] - Add task" << std::endl;
                std::cout << "    Priorities: low, medium, high, urgent" << std::endl;
                std::cout << "  update_task <id> <status>      - Update task status" << std::endl;
                std::cout << "    Status: pending, in_progress, completed, cancelled" << std::endl;
                std::cout << "  remove_task <id>               - Remove task" << std::endl;
                std::cout << "  list_tasks                     - List all tasks" << std::endl;
                std::cout << "  clear_tasks                    - Remove all tasks" << std::endl;
                std::cout << "\nSystem:" << std::endl;
                std::cout << "  start_updates                  - Start periodic updates" << std::endl;
                std::cout << "  stop_updates                   - Stop periodic updates" << std::endl;
                std::cout << "  help                           - Show this help" << std::endl;
                std::cout << "  exit                           - Exit program" << std::endl;
                std::cout << std::string(50, '=') << std::endl;
            }
            else if (command == "signup") {
                std::string username, password;
                iss >> username >> password;
                if (username.empty() || password.empty()) {
                    std::cout << "Error: Both username and password are required." << std::endl;
                    continue;
                }
                manager.signup(username, password);
            }
            else if (command == "login") {
                std::string username, password;
                iss >> username >> password;
                if (username.empty() || password.empty()) {
                    std::cout << "Error: Both username and password are required." << std::endl;
                    continue;
                }
                manager.login(username, password);
            }
            else if (command == "logout") {
                manager.logout();
            }
            else if (command == "add_event") {
                std::string name, start_time, end_time;
                iss >> name >> start_time >> end_time;

                if (name.empty() || start_time.empty() || end_time.empty()) {
                    std::cout << "Error: Event name, start time, and end time are required." << std::endl;
                    std::cout << "Format: add_event <name> <HH:MM> <HH:MM> [description]" << std::endl;
                    continue;
                }

                // Read optional description (rest of the line)
                std::string description;
                std::getline(iss >> std::ws, description);

                manager.addEvent(name, start_time, end_time, description);
            }
            else if (command == "remove_event") {
                std::string name;
                iss >> name;
                if (name.empty()) {
                    std::cout << "Error: Event name is required." << std::endl;
                    continue;
                }
                manager.removeEvent(name);
            }
            else if (command == "list_events") {
                manager.listEvents();
            }
            else if (command == "add_periodic") {
                std::string name, start_time, end_time, type_str;
                iss >> name >> start_time >> end_time >> type_str;

                if (name.empty() || start_time.empty() || end_time.empty() || type_str.empty()) {
                    std::cout << "Error: Event name, start time, end time, and type are required." << std::endl;
                    std::cout << "Format: add_periodic <name> <HH:MM> <HH:MM> <type> [description]" << std::endl;
                    std::cout << "Types: daily, weekly, monthly" << std::endl;
                    continue;
                }

                EventType type;
                if (type_str == "daily") type = EventType::DAILY;
                else if (type_str == "weekly") type = EventType::WEEKLY;
                else if (type_str == "monthly") type = EventType::MONTHLY;
                else {
                    std::cout << "Error: Invalid event type. Use: daily, weekly, or monthly" << std::endl;
                    continue;
                }

                // Read optional description (rest of the line)
                std::string description;
                std::getline(iss >> std::ws, description);

                manager.addEvent(name, start_time, end_time, description, type);
            }
            else if (command == "add_task") {
                std::string title;
                iss >> title;

                if (title.empty()) {
                    std::cout << "Error: Task title is required." << std::endl;
                    std::cout << "Format: add_task <title> [description] [priority] [deadline] [assignee]" << std::endl;
                    continue;
                }

                std::string description, priority_str, deadline_str, assignee;

                // Read optional parameters
                if (iss >> description) {
                    // Read priority if available
                    if (iss >> priority_str) {
                        // Read deadline if available
                        if (iss >> deadline_str) {
                            // Read assignee if available
                            std::getline(iss >> std::ws, assignee);
                        }
                    }
                }

                TaskPriority priority = TaskPriority::MEDIUM;
                if (!priority_str.empty()) {
                    if (priority_str == "low") priority = TaskPriority::LOW;
                    else if (priority_str == "high") priority = TaskPriority::HIGH;
                    else if (priority_str == "urgent") priority = TaskPriority::URGENT;
                    else if (priority_str != "medium") {
                        std::cout << "Warning: Invalid priority '" << priority_str << "'. Using 'medium'." << std::endl;
                    }
                }

                manager.addTask(title, description, priority, deadline_str, assignee);
            }
            else if (command == "update_task") {
                std::string id_str, status_str;
                iss >> id_str >> status_str;

                if (id_str.empty() || status_str.empty()) {
                    std::cout << "Error: Task ID and status are required." << std::endl;
                    std::cout << "Format: update_task <id> <status>" << std::endl;
                    std::cout << "Status: pending, in_progress, completed, cancelled" << std::endl;
                    continue;
                }

                int task_id;
                try {
                    task_id = std::stoi(id_str);
                } catch (const std::exception&) {
                    std::cout << "Error: Invalid task ID format." << std::endl;
                    continue;
                }

                TaskStatus status;
                if (status_str == "pending") status = TaskStatus::PENDING;
                else if (status_str == "in_progress") status = TaskStatus::IN_PROGRESS;
                else if (status_str == "completed") status = TaskStatus::COMPLETED;
                else if (status_str == "cancelled") status = TaskStatus::CANCELLED;
                else {
                    std::cout << "Error: Invalid status. Use: pending, in_progress, completed, cancelled" << std::endl;
                    continue;
                }

                manager.updateTaskStatus(task_id, status);
            }
            else if (command == "remove_task") {
                std::string id_str;
                iss >> id_str;

                if (id_str.empty()) {
                    std::cout << "Error: Task ID is required." << std::endl;
                    continue;
                }

                int task_id;
                try {
                    task_id = std::stoi(id_str);
                } catch (const std::exception&) {
                    std::cout << "Error: Invalid task ID format." << std::endl;
                    continue;
                }

                manager.removeTask(task_id);
            }
            else if (command == "list_tasks") {
                manager.listTasks();
            }
            else if (command == "clear_tasks") {
                manager.clearAllTasks();
            }
            else if (command == "start_updates") {
                manager.startPeriodicUpdates();
            }
            else if (command == "stop_updates") {
                manager.stopPeriodicUpdates();
            }
        }
        catch (const std::exception& e) {
            std::cout << "Unexpected error processing command '" << command << "': " << e.what() << std::endl;
        }
    }

    std::cout << "\nThank you for using Event Management System!" << std::endl;
    return 0;
}
