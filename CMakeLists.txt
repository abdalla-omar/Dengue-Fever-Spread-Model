cmake_minimum_required(VERSION 3.16)

project(Dengue_Fever_Spread_Model LANGUAGES CXX)

# Final executable goes under bin/
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/bin)

# Pull in the main/ folder
add_subdirectory(main)
