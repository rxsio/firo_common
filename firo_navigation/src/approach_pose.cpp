#include <memory>
#include <fstream>
#include <string>
#include <yaml-cpp/yaml.h>
#include "ament_index_cpp/get_package_share_directory.hpp"
#include "geometry_msgs/msg/pose_stamped.hpp"
#include "rclcpp/rclcpp.hpp"
/*
This node after running will once send data from dock_approach_pose.yaml as goal_pose for nav2. After that it will close itself.
*/
class SendPose : public rclcpp::Node
{
public:
  SendPose() : Node("goal_once")
  {
    this->goal_pub_ = this->create_publisher<geometry_msgs::msg::PoseStamped>("/goal_pose", 10);

    // get data from yaml
    std::string package_share_dir = ament_index_cpp::get_package_share_directory("firo_navigation");
    std::string filename = package_share_dir + "/config/dock_approach_pose.yaml";
    RCLCPP_INFO(this->get_logger(), "Getting dock approach pose from file: %s", filename.c_str());
    try {
      YAML::Node data = YAML::LoadFile(filename);
      geometry_msgs::msg::PoseStamped goal;
      goal.header.frame_id = "map"; 
      goal.header.stamp = this->now();
      goal.pose.position.x = data["position"]["x"].as<double>();
      goal.pose.position.y = data["position"]["y"].as<double>();
      goal.pose.position.z = data["position"]["z"].as<double>();
      goal.pose.orientation.x = data["orientation"]["x"].as<double>();
      goal.pose.orientation.y = data["orientation"]["y"].as<double>();
      goal.pose.orientation.z = data["orientation"]["z"].as<double>();
      goal.pose.orientation.w = data["orientation"]["w"].as<double>();

      // publish
      this->goal_pub_->publish(goal);
      RCLCPP_INFO(this->get_logger(), "Sent dock approach pose to nav2.");

    } catch (const std::exception & e) {
      RCLCPP_ERROR(this->get_logger(), "Error while loading YAML: %s", e.what());
    }

    // wait 1s more to be sure before closing node
    this->timer_ = this->create_wall_timer(
      std::chrono::seconds(1),
      [this]() {
        rclcpp::shutdown();
      }
    );

  }

private:
  // Params
  rclcpp::Publisher<geometry_msgs::msg::PoseStamped>::SharedPtr goal_pub_;
  rclcpp::TimerBase::SharedPtr timer_;
};

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  auto node = std::make_shared<SendPose>();
  rclcpp::spin(node);
  rclcpp::shutdown();
  return 0;
}