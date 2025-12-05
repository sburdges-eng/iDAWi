#include "penta/osc/OSCClient.h"
#include "penta/osc/OSCMessage.h"
#include "penta/osc/RTMessageQueue.h"
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
  #define INVALID_SOCKET -1
  #define SOCKET_ERROR -1
  using SOCKET = int;
#endif

namespace penta::osc {

struct OSCClient::SocketImpl {
    SOCKET fd = INVALID_SOCKET;
    struct sockaddr_in destAddr{};
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
        
        // Set non-blocking mode for RT-safety
#ifdef _WIN32
        u_long mode = 1;
        ioctlsocket(fd, FIONBIO, &mode);
#else
        int flags = fcntl(fd, F_GETFL, 0);
        fcntl(fd, F_SETFL, flags | O_NONBLOCK);
#endif
        
        destAddr.sin_family = AF_INET;
        destAddr.sin_port = htons(port);
        inet_pton(AF_INET, address.c_str(), &destAddr.sin_addr);
        
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
    
    bool sendData(const void* data, size_t size) noexcept {
        if (!initialized || fd == INVALID_SOCKET) return false;
        
        ssize_t sent = sendto(fd, static_cast<const char*>(data), size, 0,
                             reinterpret_cast<const struct sockaddr*>(&destAddr),
                             sizeof(destAddr));
        return sent > 0;
    }
};

OSCClient::OSCClient(const std::string& address, uint16_t port)
    : address_(address)
    , port_(port)
    , socket_(std::make_unique<SocketImpl>())
{
    socket_->init(address, port);
}

OSCClient::~OSCClient() = default;

// Helper function to build OSC message buffer
static std::vector<uint8_t> buildOSCBuffer(const std::string& address, 
                                           const char* typeTag,
                                           const void* argData,
                                           size_t argSize) {
    std::vector<uint8_t> buffer;
    
    // Add address string (null-terminated, padded to 4-byte boundary)
    buffer.insert(buffer.end(), address.begin(), address.end());
    buffer.push_back(0);
    while (buffer.size() % 4 != 0) buffer.push_back(0);
    
    // Add type tag string (starts with ',')
    buffer.push_back(',');
    size_t tagLen = strlen(typeTag);
    for (size_t i = 0; i < tagLen; i++) {
        buffer.push_back(typeTag[i]);
    }
    buffer.push_back(0);
    while (buffer.size() % 4 != 0) buffer.push_back(0);
    
    // Add argument data
    if (argData && argSize > 0) {
        const uint8_t* argBytes = static_cast<const uint8_t*>(argData);
        buffer.insert(buffer.end(), argBytes, argBytes + argSize);
    }
    
    return buffer;
}

bool OSCClient::send(const OSCMessage& message) noexcept {
    if (!socket_ || !socket_->initialized) return false;
    
    // Build OSC buffer from message
    std::vector<uint8_t> buffer;
    const std::string& addr = message.getAddress();
    
    // Add address
    buffer.insert(buffer.end(), addr.begin(), addr.end());
    buffer.push_back(0);
    while (buffer.size() % 4 != 0) buffer.push_back(0);
    
    // Build type tag
    std::string typeTag = ",";
    size_t argCount = message.getArgumentCount();
    for (size_t i = 0; i < argCount; i++) {
        const auto& arg = message.getArgument(i);
        if (std::holds_alternative<int32_t>(arg)) {
            typeTag += 'i';
        } else if (std::holds_alternative<float>(arg)) {
            typeTag += 'f';
        } else if (std::holds_alternative<std::string>(arg)) {
            typeTag += 's';
        }
    }
    
    // Add type tag
    buffer.insert(buffer.end(), typeTag.begin(), typeTag.end());
    buffer.push_back(0);
    while (buffer.size() % 4 != 0) buffer.push_back(0);
    
    // Add arguments
    for (size_t i = 0; i < argCount; i++) {
        const auto& arg = message.getArgument(i);
        if (std::holds_alternative<int32_t>(arg)) {
            int32_t val = std::get<int32_t>(arg);
            // Convert to network byte order (big endian) using safe byte copy
            uint32_t netVal = htonl(static_cast<uint32_t>(val));
            uint8_t bytes[4];
            memcpy(bytes, &netVal, 4);
            buffer.insert(buffer.end(), bytes, bytes + 4);
        } else if (std::holds_alternative<float>(arg)) {
            float val = std::get<float>(arg);
            uint32_t intVal;
            memcpy(&intVal, &val, sizeof(float));
            uint32_t netVal = htonl(intVal);
            uint8_t bytes[4];
            memcpy(bytes, &netVal, 4);
            buffer.insert(buffer.end(), bytes, bytes + 4);
        } else if (std::holds_alternative<std::string>(arg)) {
            const std::string& str = std::get<std::string>(arg);
            buffer.insert(buffer.end(), str.begin(), str.end());
            buffer.push_back(0);
            while (buffer.size() % 4 != 0) buffer.push_back(0);
        }
    }
    
    return socket_->sendData(buffer.data(), buffer.size());
}

bool OSCClient::sendFloat(const char* address, float value) noexcept {
    if (!socket_ || !socket_->initialized) return false;
    
    // Convert float to network byte order
    uint32_t intVal;
    memcpy(&intVal, &value, sizeof(float));
    uint32_t netVal = htonl(intVal);
    
    auto buffer = buildOSCBuffer(address, "f", &netVal, sizeof(netVal));
    return socket_->sendData(buffer.data(), buffer.size());
}

bool OSCClient::sendInt(const char* address, int32_t value) noexcept {
    if (!socket_ || !socket_->initialized) return false;
    
    uint32_t netVal = htonl(static_cast<uint32_t>(value));
    auto buffer = buildOSCBuffer(address, "i", &netVal, sizeof(netVal));
    return socket_->sendData(buffer.data(), buffer.size());
}

bool OSCClient::sendString(const char* address, const char* value) noexcept {
    if (!socket_ || !socket_->initialized) return false;
    
    // Build string with padding
    std::vector<uint8_t> strData;
    size_t len = strlen(value);
    strData.insert(strData.end(), value, value + len);
    strData.push_back(0);
    while (strData.size() % 4 != 0) strData.push_back(0);
    
    auto buffer = buildOSCBuffer(address, "s", strData.data(), strData.size());
    return socket_->sendData(buffer.data(), buffer.size());
}

void OSCClient::setDestination(const std::string& address, uint16_t port) {
    address_ = address;
    port_ = port;
    
    // Reinitialize socket with new destination
    if (socket_) {
        socket_->close();
        socket_->init(address, port);
    }
}

} // namespace penta::osc
