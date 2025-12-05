#include "penta/osc/OSCHub.h"

namespace penta::osc {

OSCHub::OSCHub() : OSCHub(Config{}) {}

OSCHub::OSCHub(const Config& config)
    : config_(config)
    , server_(std::make_unique<OSCServer>(config.serverAddress, config.serverPort))
    , client_(std::make_unique<OSCClient>(config.clientAddress, config.clientPort))
    , messageQueue_(std::make_unique<RTMessageQueue>(config.queueSize))
{
}

OSCHub::~OSCHub() {
    stop();
}

bool OSCHub::start() {
    if (!server_->start()) {
        return false;
    }
    
    // Client doesn't need explicit connect in current implementation
    return true;
}

void OSCHub::stop() {
    if (server_) {
        server_->stop();
    }
    
    // Client doesn't need explicit disconnect
}

bool OSCHub::sendMessage(const OSCMessage& message) noexcept {
    if (!client_) {
        return false;
    }
    return client_->send(message);
}

bool OSCHub::receiveMessage(OSCMessage& outMessage) noexcept {
    if (!server_) {
        return false;
    }
    return server_->getMessageQueue().pop(outMessage);
}

void OSCHub::registerCallback(const std::string& pattern, MessageCallback callback) {
    std::lock_guard<std::mutex> lock(callbackMutex_);
    callbacks_.push_back({pattern, std::move(callback)});
}

bool OSCHub::matchPattern(const std::string& pattern, const std::string& address) const {
    // OSC pattern matching implementation
    // Supports: * (match any sequence), ? (match single char), // (match any path segment)

    size_t pi = 0;  // pattern index
    size_t ai = 0;  // address index

    while (pi < pattern.size() && ai < address.size()) {
        char pc = pattern[pi];
        char ac = address[ai];

        if (pc == '*') {
            // Match any sequence (non-greedy within path segment)
            ++pi;
            if (pi >= pattern.size()) {
                // * at end matches rest of current segment
                while (ai < address.size() && address[ai] != '/') {
                    ++ai;
                }
                return ai == address.size() || pi == pattern.size();
            }

            // Try to match next pattern char
            while (ai < address.size() && address[ai] != '/') {
                if (matchPattern(pattern.substr(pi), address.substr(ai))) {
                    return true;
                }
                ++ai;
            }
            continue;
        }

        if (pc == '?') {
            // Match any single character (except /)
            if (ac == '/') {
                return false;
            }
            ++pi;
            ++ai;
            continue;
        }

        if (pc == '[') {
            // Character class matching
            ++pi;
            bool negate = false;
            bool matched = false;

            if (pi < pattern.size() && pattern[pi] == '!') {
                negate = true;
                ++pi;
            }

            while (pi < pattern.size() && pattern[pi] != ']') {
                if (pi + 2 < pattern.size() && pattern[pi + 1] == '-') {
                    // Range
                    if (ac >= pattern[pi] && ac <= pattern[pi + 2]) {
                        matched = true;
                    }
                    pi += 3;
                } else {
                    if (pattern[pi] == ac) {
                        matched = true;
                    }
                    ++pi;
                }
            }

            if (pi < pattern.size()) ++pi;  // Skip ]

            if (negate) matched = !matched;
            if (!matched) return false;

            ++ai;
            continue;
        }

        if (pc == '{') {
            // Brace expansion: {foo,bar,baz}
            ++pi;
            size_t braceEnd = pattern.find('}', pi);
            if (braceEnd == std::string::npos) {
                return false;
            }

            std::string options = pattern.substr(pi, braceEnd - pi);
            std::string remaining = pattern.substr(braceEnd + 1);

            // Try each option
            size_t start = 0;
            while (start < options.size()) {
                size_t comma = options.find(',', start);
                if (comma == std::string::npos) comma = options.size();

                std::string option = options.substr(start, comma - start);
                std::string testPattern = option + remaining;

                if (matchPattern(testPattern, address.substr(ai))) {
                    return true;
                }

                start = comma + 1;
            }
            return false;
        }

        // Literal match
        if (pc != ac) {
            return false;
        }

        ++pi;
        ++ai;
    }

    // Handle trailing wildcards
    while (pi < pattern.size() && pattern[pi] == '*') {
        ++pi;
    }

    return pi == pattern.size() && ai == address.size();
}

void OSCHub::dispatchMessage(const OSCMessage& message) {
    std::lock_guard<std::mutex> lock(callbackMutex_);

    for (const auto& entry : callbacks_) {
        if (matchPattern(entry.pattern, message.getAddress())) {
            if (entry.callback) {
                entry.callback(message);
            }
        }
    }
}

void OSCHub::updateConfig(const Config& config) {
    bool wasRunning = false;
    
    if (server_ && server_->isRunning()) {
        wasRunning = true;
        stop();
    }
    
    config_ = config;
    
    // Recreate server and client with new config
    server_ = std::make_unique<OSCServer>(config.serverAddress, config.serverPort);
    client_ = std::make_unique<OSCClient>(config.clientAddress, config.clientPort);
    messageQueue_ = std::make_unique<RTMessageQueue>(config.queueSize);
    
    if (wasRunning) {
        start();
    }
}

} // namespace penta::osc
