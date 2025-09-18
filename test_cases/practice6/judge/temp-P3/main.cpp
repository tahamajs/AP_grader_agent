#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
#include <sstream>

struct Event {
    std::string name;
    std::string start_time;
    std::string end_time;

    // Convert time string to minutes since midnight for comparison
    int getStartMinutes() const {
        int hours, minutes;
        sscanf(start_time.c_str(), "%d:%d", &hours, &minutes);
        return hours * 60 + minutes;
    }

    int getEndMinutes() const {
        int hours, minutes;
        sscanf(end_time.c_str(), "%d:%d", &hours, &minutes);
        return hours * 60 + minutes;
    }
};

class EventManager {
private:
    std::vector<Event> events;

    // Check if two time ranges overlap
    bool hasTimeConflict(const Event& new_event) const {
        int new_start = new_event.getStartMinutes();
        int new_end = new_event.getEndMinutes();

        for (const auto& existing : events) {
            int existing_start = existing.getStartMinutes();
            int existing_end = existing.getEndMinutes();

            // Check for overlap: new event starts before existing ends AND new event ends after existing starts
            if (new_start < existing_end && new_end > existing_start) {
                return true;
            }
        }
        return false;
    }

    // Sort events by start time
    static bool compareByStartTime(const Event& a, const Event& b) {
        return a.getStartMinutes() < b.getStartMinutes();
    }

public:
    bool addEvent(const std::string& name, const std::string& start_time, const std::string& end_time) {
        Event new_event = {name, start_time, end_time};

        if (hasTimeConflict(new_event)) {
            std::cout << "Time conflict detected" << std::endl;
            return false;
        }

        events.push_back(new_event);
        std::cout << "Event added successfully" << std::endl;
        return true;
    }

    bool removeEvent(const std::string& name) {
        auto it = std::find_if(events.begin(), events.end(),
            [&name](const Event& e) { return e.name == name; });

        if (it != events.end()) {
            events.erase(it);
            std::cout << "Event removed successfully" << std::endl;
            return true;
        }

        std::cout << "Event not found" << std::endl;
        return false;
    }

    void listEvents() const {
        if (events.empty()) {
            std::cout << "No events scheduled" << std::endl;
            return;
        }

        // Create a copy and sort it
        std::vector<Event> sorted_events = events;
        std::sort(sorted_events.begin(), sorted_events.end(), compareByStartTime);

        std::cout << "Events:" << std::endl;
        for (const auto& event : sorted_events) {
            std::cout << "- " << event.name << ": " << event.start_time << " - " << event.end_time << std::endl;
        }
    }
};

int main() {
    EventManager manager;
    std::string line;

    while (std::getline(std::cin, line)) {
        // Exit on empty line
        if (line.empty()) {
            break;
        }

        std::istringstream iss(line);
        std::string command;
        iss >> command;

        if (command == "add_event") {
            std::string name, start_time, end_time;
            iss >> name >> start_time >> end_time;
            if (name.empty() || start_time.empty() || end_time.empty()) {
                std::cout << "Invalid command format" << std::endl;
                continue;
            }
            manager.addEvent(name, start_time, end_time);
        }
        else if (command == "remove_event") {
            std::string name;
            iss >> name;
            if (name.empty()) {
                std::cout << "Invalid command format" << std::endl;
                continue;
            }
            manager.removeEvent(name);
        }
        else if (command == "list_events") {
            manager.listEvents();
        }
        else {
            std::cout << "Unknown command" << std::endl;
        }
    }

    return 0;
}
