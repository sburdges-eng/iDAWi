#include "penta/osc/OSCServer.h"
#include "penta/osc/OSCMessage.h"
#include <cstring>
#include <vector>

#ifdef _WIN32
  #include <winsock2.h>
  #include <ws2tcpip.h>
  #pragma comment(lib, "ws2_32.lib")
#else
  #include <sys/socket.h>
  #include <netinet/in.h>
  #include <arpa/inet.h>
  #include <unistd.h>
  #include <fcntl.h>
  #include <poll.h>
  #define INVALID_SOCKET -1
  #define SOCKET_ERROR -1
  using SOCKET = int;
#endif

namespace penta::osc {

struct OSCServer::SocketImpl {
    SOCKET fd = INVALID_SOCKET;
    struct sockaddr_in bindAddr{};
    bool initialized = false;
    
    SocketImpl() = default;
    
    ~SocketImpl() {
        close();
    }
    
    bool init(const std::string& address, uint16_t port) {
#ifdef _WIN32
        WSADATA wsaData;
        if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0) {
            return false;
        }
#endif
        fd = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
        if (fd == INVALID_SOCKET) {
            return false;
        }
        
        // Allow address reuse
        int opt = 1;
#ifdef _WIN32
        setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, reinterpret_cast<const char*>(&opt), sizeof(opt));
#else
        setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
#endif
        
        bindAddr.sin_family = AF_INET;
        bindAddr.sin_port = htons(port);
        if (address.empty() || address == "0.0.0.0") {
            bindAddr.sin_addr.s_addr = INADDR_ANY;
        } else {
            inet_pton(AF_INET, address.c_str(), &bindAddr.sin_addr);
        }
        
        if (bind(fd, reinterpret_cast<struct sockaddr*>(&bindAddr), sizeof(bindAddr)) < 0) {
            close();
            return false;
        }
        
        initialized = true;
        return true;
    }
    
    void close() {
        if (fd != INVALID_SOCKET) {
#ifdef _WIN32
            closesocket(fd);
            WSACleanup();
#else
            ::close(fd);
#endif
            fd = INVALID_SOCKET;
        }
        initialized = false;
    }
    
    ssize_t receiveData(void* buffer, size_t maxSize, int timeoutMs) {
        if (!initialized || fd == INVALID_SOCKET) return -1;
        
#ifdef _WIN32
        fd_set readSet;
        FD_ZERO(&readSet);
        FD_SET(fd, &readSet);
        struct timeval tv;
        tv.tv_sec = timeoutMs / 1000;
        tv.tv_usec = (timeoutMs % 1000) * 1000;
        
        int result = select(1, &readSet, nullptr, nullptr, &tv);
        if (result <= 0) return result;
#else
        struct pollfd pfd;
        pfd.fd = fd;
        pfd.events = POLLIN;
        int result = poll(&pfd, 1, timeoutMs);
        if (result <= 0) return result;
#endif
        
        struct sockaddr_in srcAddr;
        socklen_t addrLen = sizeof(srcAddr);
        return recvfrom(fd, static_cast<char*>(buffer), maxSize, 0,
                       reinterpret_cast<struct sockaddr*>(&srcAddr), &addrLen);
    }
};

// Helper to parse OSC message from buffer
static bool parseOSCMessage(const uint8_t* data, size_t size, OSCMessage& msg) {
    if (!data || size < 4) return false;
    
    // Find null terminator for address
    size_t addrEnd = 0;
    while (addrEnd < size && data[addrEnd] != 0) addrEnd++;
    if (addrEnd == 0 || addrEnd >= size) return false;
    
    std::string address(reinterpret_cast<const char*>(data), addrEnd);
    msg.setAddress(address);
    
    // Skip to 4-byte boundary
    size_t pos = ((addrEnd + 4) / 4) * 4;
    if (pos >= size) return true;  // No type tag or arguments
    
    // Check for type tag
    if (data[pos] != ',') return true;  // No type tag
    
    // Find type tag
    size_t typeTagStart = pos + 1;
    size_t typeTagEnd = typeTagStart;
    while (typeTagEnd < size && data[typeTagEnd] != 0) typeTagEnd++;
    
    std::string typeTag(reinterpret_cast<const char*>(data + typeTagStart), 
                       typeTagEnd - typeTagStart);
    
    // Skip to arguments
    pos = ((typeTagEnd + 4) / 4) * 4;
    
    // Parse arguments based on type tag
    for (char type : typeTag) {
        if (pos + 4 > size && type != 's') break;
        
        switch (type) {
            case 'i': {  // int32
                uint32_t netVal;
                memcpy(&netVal, data + pos, 4);
                int32_t val = static_cast<int32_t>(ntohl(netVal));
                msg.addInt(val);
                pos += 4;
                break;
            }
            case 'f': {  // float
                uint32_t netVal;
                memcpy(&netVal, data + pos, 4);
                uint32_t hostVal = ntohl(netVal);
                float val;
                memcpy(&val, &hostVal, sizeof(float));
                msg.addFloat(val);
                pos += 4;
                break;
            }
            case 's': {  // string
                size_t strEnd = pos;
                while (strEnd < size && data[strEnd] != 0) strEnd++;
                std::string str(reinterpret_cast<const char*>(data + pos), strEnd - pos);
                msg.addString(str);
                pos = ((strEnd + 4) / 4) * 4;
                break;
            }
            default:
                // Unknown type, skip
                break;
        }
    }
    
    return true;
}

OSCServer::OSCServer(const std::string& address, uint16_t port)
    : address_(address)
    , port_(port)
    , running_(false)
    , messageQueue_(std::make_unique<RTMessageQueue>(4096))
    , socket_(std::make_unique<SocketImpl>())
{
}

OSCServer::~OSCServer() {
    stop();
}

bool OSCServer::start() {
    if (running_.load(std::memory_order_acquire)) {
        return true;  // Already running
    }
    
    if (!socket_->init(address_, port_)) {
        return false;
    }
    
    running_.store(true, std::memory_order_release);
    receiveThread_ = std::thread(&OSCServer::receiveThread, this);
    
    return true;
}

void OSCServer::stop() {
    if (!running_.load(std::memory_order_acquire)) {
        return;
    }
    
    running_.store(false, std::memory_order_release);
    
    if (receiveThread_.joinable()) {
        receiveThread_.join();
    }
    
    socket_->close();
}

void OSCServer::receiveThread() {
    std::vector<uint8_t> buffer(65536);  // Max UDP packet size
    
    while (running_.load(std::memory_order_acquire)) {
        ssize_t received = socket_->receiveData(buffer.data(), buffer.size(), 100);
        
        if (received > 0) {
            OSCMessage msg;
            if (parseOSCMessage(buffer.data(), static_cast<size_t>(received), msg)) {
                // Push message to lock-free queue
                messageQueue_->push(msg);
            }
        }
    }
}

} // namespace penta::osc
