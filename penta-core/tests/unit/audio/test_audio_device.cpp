#include <gtest/gtest.h>
#include "penta/audio/AudioDevice.h"
#include <thread>
#include <chrono>
#include <vector>

using namespace penta::audio;

class AudioDeviceTest : public ::testing::Test {
protected:
    std::unique_ptr<AudioDevice> device;

    void SetUp() override {
        device = createAudioDevice();
        ASSERT_NE(device, nullptr) << "Failed to create audio device";
    }

    void TearDown() override {
        if (device && device->isRunning()) {
            EXPECT_TRUE(device->stop());
        }
    }
};

// Test 1: Device enumeration
TEST_F(AudioDeviceTest, EnumerateInputDevices) {
    auto devices = device->enumerateInputDevices();
    EXPECT_GT(devices.size(), 0) << "Should find at least one input device";

    for (const auto& dev : devices) {
        EXPECT_FALSE(dev.name.empty());
        EXPECT_FALSE(dev.driver.empty());
        EXPECT_GT(dev.sample_rates.size(), 0);
        EXPECT_TRUE(dev.is_input);
    }
}

TEST_F(AudioDeviceTest, EnumerateOutputDevices) {
    auto devices = device->enumerateOutputDevices();
    EXPECT_GT(devices.size(), 0) << "Should find at least one output device";

    for (const auto& dev : devices) {
        EXPECT_FALSE(dev.name.empty());
        EXPECT_FALSE(dev.driver.empty());
        EXPECT_GT(dev.sample_rates.size(), 0);
        EXPECT_FALSE(dev.is_input);
    }
}

TEST_F(AudioDeviceTest, GetDefaultInputDevice) {
    auto device_opt = device->getDefaultInputDevice();
    EXPECT_TRUE(device_opt.has_value());
    if (device_opt) {
        EXPECT_FALSE(device_opt->name.empty());
        EXPECT_TRUE(device_opt->is_input);
    }
}

TEST_F(AudioDeviceTest, GetDefaultOutputDevice) {
    auto device_opt = device->getDefaultOutputDevice();
    EXPECT_TRUE(device_opt.has_value());
    if (device_opt) {
        EXPECT_FALSE(device_opt->name.empty());
        EXPECT_FALSE(device_opt->is_input);
    }
}

// Test 2: Configuration
TEST_F(AudioDeviceTest, SetSampleRate) {
    std::vector<uint32_t> rates = {44100, 48000, 96000};
    for (uint32_t rate : rates) {
        EXPECT_TRUE(device->setSampleRate(rate));
        EXPECT_EQ(device->getSampleRate(), rate)
            << "Sample rate " << rate << " not set correctly";
    }
}

TEST_F(AudioDeviceTest, SetBufferSize) {
    std::vector<uint32_t> sizes = {64, 128, 256, 512};
    for (uint32_t size : sizes) {
        EXPECT_TRUE(device->setBufferSize(size));
        EXPECT_EQ(device->getBufferSize(), size)
            << "Buffer size " << size << " not set correctly";
    }
}

// Test 3: Start/Stop
TEST_F(AudioDeviceTest, StartStop) {
    EXPECT_FALSE(device->isRunning()) << "Device should not be running initially";

    EXPECT_TRUE(device->start()) << "Failed to start device";
    EXPECT_TRUE(device->isRunning()) << "Device should be running after start()";
    EXPECT_TRUE(device->isInitialized()) << "Device should be initialized";

    EXPECT_TRUE(device->stop()) << "Failed to stop device";
    EXPECT_FALSE(device->isRunning()) << "Device should not be running after stop()";
}

TEST_F(AudioDeviceTest, MultipleStartStop) {
    for (int i = 0; i < 5; ++i) {
        EXPECT_TRUE(device->start());
        EXPECT_TRUE(device->isRunning());
        EXPECT_TRUE(device->stop());
        EXPECT_FALSE(device->isRunning());
    }
}

// Test 4: Latency measurement
TEST_F(AudioDeviceTest, LatencyMeasurement) {
    EXPECT_TRUE(device->start());

    float latency_in_ms = device->getInputLatencyMs();
    float latency_out_ms = device->getOutputLatencyMs();
    uint32_t latency_in_samples = device->getInputLatencySamples();
    uint32_t latency_out_samples = device->getOutputLatencySamples();

    EXPECT_GT(latency_in_ms, 0) << "Input latency should be > 0";
    EXPECT_LT(latency_in_ms, 500) << "Input latency should be < 500ms";
    EXPECT_GT(latency_out_ms, 0) << "Output latency should be > 0";
    EXPECT_LT(latency_out_ms, 500) << "Output latency should be < 500ms";

    EXPECT_GT(latency_in_samples, 0);
    EXPECT_GT(latency_out_samples, 0);

    std::cout << "Input Latency: " << latency_in_ms << "ms ("
              << latency_in_samples << " samples)\n";
    std::cout << "Output Latency: " << latency_out_ms << "ms ("
              << latency_out_samples << " samples)\n";

    EXPECT_TRUE(device->stop());
}

// Test 5: Audio callback
TEST_F(AudioDeviceTest, AudioCallback) {
    bool callback_called = false;
    uint32_t total_samples = 0;
    int callback_count = 0;

    device->setAudioCallback([&](const float* const* inputs,
                                 float* const* outputs,
                                 uint32_t num_samples,
                                 double sample_time) {
        callback_called = true;
        total_samples += num_samples;
        callback_count++;

        // Simple passthrough
        if (inputs && inputs[0] && outputs && outputs[0]) {
            std::copy(inputs[0], inputs[0] + num_samples, outputs[0]);
        }
    });

    EXPECT_TRUE(device->start());

    // Wait for callbacks
    std::this_thread::sleep_for(std::chrono::milliseconds(100));

    EXPECT_TRUE(callback_called) << "Audio callback should be called";
    EXPECT_GT(callback_count, 0) << "Should process multiple callbacks";
    EXPECT_GT(total_samples, 0) << "Should process samples";

    std::cout << "Processed " << callback_count << " callbacks, "
              << total_samples << " total samples\n";

    EXPECT_TRUE(device->stop());
}

// Test 6: Error callback
TEST_F(AudioDeviceTest, ErrorCallback) {
    std::string last_error;
    device->setErrorCallback([&](const std::string& error) {
        last_error = error;
        std::cout << "Error: " << error << "\n";
    });

    EXPECT_TRUE(device->start());
    std::this_thread::sleep_for(std::chrono::milliseconds(50));
    EXPECT_TRUE(device->stop());

    // Should not have errors in normal operation
    EXPECT_TRUE(last_error.empty())
        << "Should not have errors in normal operation";
}

// Test 7: Device names
TEST_F(AudioDeviceTest, DeviceNames) {
    std::string input_name = device->getInputDeviceName();
    std::string output_name = device->getOutputDeviceName();

    EXPECT_FALSE(input_name.empty());
    EXPECT_FALSE(output_name.empty());

    std::cout << "Input Device: " << input_name << "\n";
    std::cout << "Output Device: " << output_name << "\n";
}

// Test 8: Channel configuration
TEST_F(AudioDeviceTest, ChannelConfiguration) {
    uint32_t input_channels = device->getInputChannels();
    uint32_t output_channels = device->getOutputChannels();

    EXPECT_GT(input_channels, 0);
    EXPECT_GT(output_channels, 0);

    std::cout << "Input Channels: " << input_channels << "\n";
    std::cout << "Output Channels: " << output_channels << "\n";
}

// Test 9: CPU load
TEST_F(AudioDeviceTest, CPULoad) {
    EXPECT_TRUE(device->start());

    float cpu_load = device->getCpuLoad();
    EXPECT_GE(cpu_load, 0.0f);
    EXPECT_LE(cpu_load, 1.0f);

    bool overloaded = device->isCpuOverloaded();
    EXPECT_FALSE(overloaded)
        << "CPU should not be overloaded in idle state";

    std::cout << "CPU Load: " << (cpu_load * 100.0f) << "%\n";

    EXPECT_TRUE(device->stop());
}

// Test 10: Device selection
TEST_F(AudioDeviceTest, SelectDevices) {
    auto input_devices = device->enumerateInputDevices();
    auto output_devices = device->enumerateOutputDevices();

    if (!input_devices.empty()) {
        EXPECT_TRUE(device->selectInputDevice(input_devices[0].id));
    }

    if (!output_devices.empty()) {
        EXPECT_TRUE(device->selectOutputDevice(output_devices[0].id));
    }

    EXPECT_TRUE(device->start());
    EXPECT_TRUE(device->stop());
}

// Stress test
TEST_F(AudioDeviceTest, StressTest) {
    // Start/stop 10 times
    for (int i = 0; i < 10; ++i) {
        EXPECT_TRUE(device->start());
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
        EXPECT_TRUE(device->stop());
    }
}

// Latency consistency test
TEST_F(AudioDeviceTest, LatencyConsistency) {
    EXPECT_TRUE(device->setSampleRate(48000));
    EXPECT_TRUE(device->setBufferSize(256));

    EXPECT_TRUE(device->start());

    std::vector<float> latencies_ms;
    for (int i = 0; i < 5; ++i) {
        latencies_ms.push_back(device->getInputLatencyMs());
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }

    // All latency measurements should be identical
    for (size_t i = 1; i < latencies_ms.size(); ++i) {
        EXPECT_EQ(latencies_ms[i], latencies_ms[0])
            << "Latency should be consistent";
    }

    EXPECT_TRUE(device->stop());
}

int main(int argc, char** argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
