cmake_minimum_required(VERSION 3.22.1...3.30.1)
project(firo_description)
find_package(ament_cmake REQUIRED)
install(DIRECTORY launch DESTINATION share/${PROJECT_NAME}/)
install(DIRECTORY urdf DESTINATION share/${PROJECT_NAME}/)
install(DIRECTORY robots DESTINATION share/${PROJECT_NAME}/)
install(DIRECTORY meshes DESTINATION share/${PROJECT_NAME}/)
install(DIRECTORY config DESTINATION share/${PROJECT_NAME}/)

ament_environment_hooks("${CMAKE_CURRENT_SOURCE_DIR}/hooks/${PROJECT_NAME}.dsv.in")
ament_environment_hooks("${CMAKE_CURRENT_SOURCE_DIR}/hooks/${PROJECT_NAME}.sh.in")

ament_package()
