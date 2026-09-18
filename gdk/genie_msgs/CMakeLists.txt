cmake_minimum_required(VERSION 3.8)
project(genie_msgs)

# 查找必要的包
find_package(ros2 QUIET)
find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(builtin_interfaces REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(shape_msgs REQUIRED)
find_package(std_msgs REQUIRED)

# 设置C++标准
if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 14)
endif()

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# 递归查找所有的.msg和.srv文件
file(GLOB_RECURSE MSG_FILES RELATIVE ${CMAKE_CURRENT_SOURCE_DIR} "msg/*.msg")
file(GLOB_RECURSE SRV_FILES RELATIVE ${CMAKE_CURRENT_SOURCE_DIR} "srv/*.srv")

# 生成接口
rosidl_generate_interfaces(${PROJECT_NAME}
  ${MSG_FILES}
  ${SRV_FILES}
  DEPENDENCIES
    builtin_interfaces
    geometry_msgs
    nav_msgs
    sensor_msgs
    shape_msgs
    std_msgs
)

ament_export_dependencies(rosidl_default_runtime)

ament_package()

