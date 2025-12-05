cmake_minimum_required(VERSION 3.20)
project(PentaCoreTests)

include(GoogleTest)

# Test sources - Core modules (Phase 0)
set(TEST_SOURCES
    harmony_test.cpp
    groove_test.cpp
    osc_test.cpp
    rt_memory_test.cpp
)

# Test sources - MIDI module (Phase 1 Week 3-4)
set(MIDI_TEST_SOURCES
    unit/midi/MIDITypesTest.cpp
    unit/midi/MIDIBufferTest.cpp
)

# Test sources - Transport module (Phase 1 Week 5-6)
set(TRANSPORT_TEST_SOURCES
    unit/transport/TransportTest.cpp
)

# Main test executable
add_executable(penta_tests
    ${TEST_SOURCES}
    ${MIDI_TEST_SOURCES}
    ${TRANSPORT_TEST_SOURCES}
)

target_link_libraries(penta_tests PRIVATE
    penta_core
    gtest
    gtest_main
)

# Enable threading for tests
if(UNIX)
    target_link_libraries(penta_tests PRIVATE pthread)
endif()

# Discover tests for CTest
gtest_discover_tests(penta_tests)
