#include <memory>
#include <string>
#include <vector>
#include <fstream>
#include <ament_index_cpp/get_package_share_directory.hpp>
#include <yaml-cpp/yaml.h>
#include <nav_msgs/msg/odometry.hpp>
#include "rclcpp/rclcpp.hpp"
/*
This node after running will once get the data from ekf/global and save it into dock_approach_pose.yaml in config folder. After that it will close itself.
*/

class PoseSaver : public rclcpp::Node
{
public:
  PoseSaver() : Node("approach_pose_saver")
  {
    // Subscribers
    this->subscriber_pose_ = this->create_subscription<nav_msgs::msg::Odometry>(
      "/ekf/global", 10, std::bind(&PoseSaver::PoseCallback, this, std::placeholders::_1));
    RCLCPP_INFO(this->get_logger(), "Waiting to recieve current pose on map to save...");
  }

private:
  void PoseCallback(const nav_msgs::msg::Odometry & msg)
  {
    YAML::Node data;
    data["position"]["x"] = msg.pose.pose.position.x;
    data["position"]["y"] = msg.pose.pose.position.y;
    data["position"]["z"] = msg.pose.pose.position.z;

    data["orientation"]["x"] = msg.pose.pose.orientation.x;
    data["orientation"]["y"] = msg.pose.pose.orientation.y;
    data["orientation"]["z"] = msg.pose.pose.orientation.z;
    data["orientation"]["w"] = msg.pose.pose.orientation.w;

    // save into yaml file
    std::string package_share_dir = ament_index_cpp::get_package_share_directory("firo_navigation");
    std::string filename = package_share_dir + "/config/dock_approach_pose.yaml";
    std::ofstream fout(filename, std::ios::trunc);
    fout << data;
    fout.close();
    RCLCPP_INFO(this->get_logger(), "Saved dock approach pose in file: %s", filename.c_str());
    // close the node
    rclcpp::shutdown();
  }

  // Params 
  rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr subscriber_pose_;
};

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  auto node = std::make_shared<PoseSaver>();
  rclcpp::spin(node);
  rclcpp::shutdown();
  return 0;
}
