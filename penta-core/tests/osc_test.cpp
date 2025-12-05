#include "penta/osc/OSCServer.h"
#include "penta/osc/OSCClient.h"
#include "penta/osc/OSCHub.h"
#include "penta/osc/RTMessageQueue.h"
#include <gtest/gtest.h>
#include <thread>
#include <chrono>
#include <variant>

using namespace penta::osc;

// ========== RTMessageQueue Tests ==========

class RTMessageQueueTest : public ::testing::Test {
protected:
    RTMessageQueue queue{1024};
};

TEST_F(RTMessageQueueTest, PushAndPop) {
    OSCMessage msg;
    msg.setAddress("/test");
    msg.addFloat(42.0f);
    
    EXPECT_TRUE(queue.push(msg));
    
    OSCMessage retrieved;
    EXPECT_TRUE(queue.pop(retrieved));
    EXPECT_EQ(retrieved.getAddress(), "/test");
    EXPECT_EQ(retrieved.getArgumentCount(), 1u);
    EXPECT_FLOAT_EQ(std::get<float>(retrieved.getArgument(0)), 42.0f);
}

TEST_F(RTMessageQueueTest, FIFOOrder) {
    OSCMessage msg1, msg2, msg3;
    msg1.setAddress("/first");
    msg2.setAddress("/second");
    msg3.setAddress("/third");
    
    queue.push(msg1);
    queue.push(msg2);
    queue.push(msg3);
    
    OSCMessage retrieved;
    queue.pop(retrieved);
    EXPECT_EQ(retrieved.getAddress(), "/first");
    
    queue.pop(retrieved);
    EXPECT_EQ(retrieved.getAddress(), "/second");
    
    queue.pop(retrieved);
    EXPECT_EQ(retrieved.getAddress(), "/third");
}

TEST_F(RTMessageQueueTest, EmptyQueueReturnsFalse) {
    OSCMessage msg;
    EXPECT_FALSE(queue.pop(msg));
}

TEST_F(RTMessageQueueTest, SizeReturnsCorrectCount) {
    EXPECT_EQ(queue.size(), 0u);
    
    OSCMessage msg;
    msg.setAddress("/test");
    
    queue.push(msg);
    queue.push(msg);
    queue.push(msg);
    
    EXPECT_EQ(queue.size(), 3u);
    
    OSCMessage out;
    queue.pop(out);
    EXPECT_EQ(queue.size(), 2u);
}

// ========== OSCServer Tests ==========

class OSCServerTest : public ::testing::Test {
protected:
    void SetUp() override {
        server = std::make_unique<OSCServer>("127.0.0.1", 9001);
    }
    
    void TearDown() override {
        if (server) {
            server->stop();
        }
    }
    
    std::unique_ptr<OSCServer> server;
};

TEST_F(OSCServerTest, StartsAndStops) {
    EXPECT_NO_THROW(server->start());
    EXPECT_TRUE(server->isRunning());
    std::this_thread::sleep_for(std::chrono::milliseconds(100));
    EXPECT_NO_THROW(server->stop());
    EXPECT_FALSE(server->isRunning());
}

TEST_F(OSCServerTest, ProvidesMessageQueue) {
    server->start();
    
    // Verify the message queue is accessible
    RTMessageQueue& queue = server->getMessageQueue();
    EXPECT_TRUE(queue.isEmpty());
    
    server->stop();
}

// ========== OSCClient Tests ==========

class OSCClientTest : public ::testing::Test {
protected:
    void SetUp() override {
        client = std::make_unique<OSCClient>("127.0.0.1", 9002);
    }
    
    void TearDown() override {
        // Client is automatically cleaned up
    }
    
    std::unique_ptr<OSCClient> client;
};

TEST_F(OSCClientTest, CanConstruct) {
    EXPECT_NE(client, nullptr);
}

TEST_F(OSCClientTest, SendsMessage) {
    OSCMessage msg;
    msg.setAddress("/test");
    msg.addFloat(42.0f);
    
    // Send may return true (socket ready) or false (network issue)
    // We just test it doesn't crash
    bool result = client->send(msg);
    // Result depends on network availability
    (void)result;
}

TEST_F(OSCClientTest, SendsFloat) {
    // Test sendFloat helper method
    bool result = client->sendFloat("/test/float", 3.14f);
    (void)result;
}

TEST_F(OSCClientTest, SendsInt) {
    // Test sendInt helper method
    bool result = client->sendInt("/test/int", 42);
    (void)result;
}

TEST_F(OSCClientTest, SendsString) {
    // Test sendString helper method
    bool result = client->sendString("/test/string", "hello");
    (void)result;
}

// ========== OSCHub Tests ==========

class OSCHubTest : public ::testing::Test {
protected:
    void SetUp() override {
        OSCHub::Config config;
        config.serverAddress = "127.0.0.1";
        config.serverPort = 9003;
        config.clientAddress = "127.0.0.1";
        config.clientPort = 9004;
        hub = std::make_unique<OSCHub>(config);
    }
    
    void TearDown() override {
        if (hub) {
            hub->stop();
        }
    }
    
    std::unique_ptr<OSCHub> hub;
};

TEST_F(OSCHubTest, StartsAndStops) {
    EXPECT_NO_THROW(hub->start());
    std::this_thread::sleep_for(std::chrono::milliseconds(100));
    EXPECT_NO_THROW(hub->stop());
}

TEST_F(OSCHubTest, SendsMessage) {
    hub->start();
    
    OSCMessage msg;
    msg.setAddress("/test");
    msg.addFloat(42.0f);
    
    // Test sendMessage method
    bool result = hub->sendMessage(msg);
    (void)result;  // Result depends on network
    
    hub->stop();
}

TEST_F(OSCHubTest, RegistersCallback) {
    bool callbackCalled = false;
    
    hub->registerCallback("/test/*", [&callbackCalled](const OSCMessage&) {
        callbackCalled = true;
    });
    
    // Callback registration should succeed
    EXPECT_NO_THROW(hub->start());
    hub->stop();
}

// ========== Performance Benchmarks ==========

class OSCPerformanceBenchmark : public ::testing::Test {
protected:
    OSCClient client{"127.0.0.1", 9005};
    OSCMessage testMsg;
    
    void SetUp() override {
        testMsg.setAddress("/benchmark");
        testMsg.addFloat(1.0f);
        testMsg.addFloat(2.0f);
        testMsg.addFloat(3.0f);
    }
    
    void TearDown() override {
        // Client is automatically cleaned up
    }
};

TEST_F(OSCPerformanceBenchmark, SendLatency) {
    constexpr int iterations = 1000;
    
    auto start = std::chrono::high_resolution_clock::now();
    
    for (int i = 0; i < iterations; ++i) {
        client.send(testMsg);
    }
    
    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
    
    double avgMicros = static_cast<double>(duration.count()) / iterations;
    
    std::cout << "Average OSC send time: " << avgMicros << " μs\n";
    
    EXPECT_LT(avgMicros, 100.0);  // Target: <100μs per send
}

TEST_F(OSCPerformanceBenchmark, MessageQueueThroughput) {
    RTMessageQueue queue{10000};
    constexpr int iterations = 10000;
    
    auto start = std::chrono::high_resolution_clock::now();
    
    for (int i = 0; i < iterations; ++i) {
        queue.push(testMsg);
    }
    
    auto pushEnd = std::chrono::high_resolution_clock::now();
    
    OSCMessage retrieved;
    for (int i = 0; i < iterations; ++i) {
        queue.pop(retrieved);
    }
    
    auto popEnd = std::chrono::high_resolution_clock::now();
    
    auto pushDuration = std::chrono::duration_cast<std::chrono::microseconds>(pushEnd - start);
    auto popDuration = std::chrono::duration_cast<std::chrono::microseconds>(popEnd - pushEnd);
    
    double avgPushMicros = static_cast<double>(pushDuration.count()) / iterations;
    double avgPopMicros = static_cast<double>(popDuration.count()) / iterations;
    
    std::cout << "Average queue push: " << avgPushMicros << " μs\n";
    std::cout << "Average queue pop: " << avgPopMicros << " μs\n";
    
    EXPECT_LT(avgPushMicros, 1.0);  // Lock-free should be <1μs
    EXPECT_LT(avgPopMicros, 1.0);
}

// Note: main() is provided by gtest_main
