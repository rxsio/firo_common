cmake_minimum_required(VERSION 3.8)
project(firo_navigation)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(ament_index_cpp REQUIRED)
# uncomment the following section in order to fill in
# further dependencies manually.
# find_package(<dependency> REQUIRED)
find_package(navigation2 REQUIRED)
find_package(slam_toolbox REQUIRED)
find_package(robot_localization REQUIRED)
find_package(yaml-cpp REQUIRED)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # the following line skips the linter which checks for copyrights
  # comment the line when a copyright and license is added to all source files
  set(ament_cmake_copyright_FOUND TRUE)
  # the following line skips cpplint (only works in a git repo)
  # comment the line when this package is in a git repo and when
  # a copyright and license is added to all source files
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

add_executable(odometry_fixer_node src/odometry_fixer_node.cpp)
add_executable(command_twist_stamper_node src/command_twist_stamper_node.cpp)
add_executable(lidar_vertical_filter src/lidar_vertical_filter.cpp)
add_executable(dock_approach_manager src/dock_approach_manager.cpp)

target_link_libraries(dock_approach_manager yaml-cpp)

ament_target_dependencies(odometry_fixer_node rclcpp nav_msgs)
ament_target_dependencies(command_twist_stamper_node rclcpp geometry_msgs action_msgs)
ament_target_dependencies(lidar_vertical_filter rclcpp sensor_msgs)
ament_target_dependencies(dock_approach_manager rclcpp  geometry_msgs  std_srvs  tf2_ros  tf2  yaml-cpp  ament_index_cpp)

install(TARGETS odometry_fixer_node command_twist_stamper_node lidar_vertical_filter dock_approach_manager DESTINATION lib/${PROJECT_NAME})

install(DIRECTORY config DESTINATION share/${PROJECT_NAME})

install(DIRECTORY launch DESTINATION share/${PROJECT_NAME})

install(DIRECTORY src DESTINATION share/${PROJECT_NAME})

ament_package()
