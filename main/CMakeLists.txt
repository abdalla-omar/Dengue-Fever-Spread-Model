# main/CMakeLists.txt
cmake_minimum_required(VERSION 3.16)
project(Dengue_Fever_Spread_Model LANGUAGES CXX)

# 1) Build the executable
add_executable(${PROJECT_NAME}
  "${CMAKE_CURRENT_SOURCE_DIR}/main.cpp"
)

# 2) Require CADMIUM env var to point at your cadmium_v2 repo root
if(NOT DEFINED ENV{CADMIUM} OR "$ENV{CADMIUM}" STREQUAL "")
  message(FATAL_ERROR "Please set the CADMIUM environment variable to your cadmium_v2 repo root")
endif()
set(CADMIUM_DIR "$ENV{CADMIUM}")

# 3) Header search paths
target_include_directories(${PROJECT_NAME} PUBLIC
  "${CMAKE_CURRENT_SOURCE_DIR}/main/include"  # your headers
  "${CADMIUM_DIR}/include"               # Cadmium headers
)

# 4) Find and link nlohmann_json (system-installed)
find_package(nlohmann_json 3.2.0 REQUIRED)
target_link_libraries(${PROJECT_NAME} PUBLIC nlohmann_json::nlohmann_json)

# 5) Enforce C++20
set_target_properties(${PROJECT_NAME} PROPERTIES
  CXX_STANDARD        20
  CXX_STANDARD_REQUIRED ON
  CXX_EXTENSIONS      OFF
)

# 6) Extra warning flags
target_compile_options(${PROJECT_NAME} PUBLIC
  -Wall -Wextra -Wpedantic
)
