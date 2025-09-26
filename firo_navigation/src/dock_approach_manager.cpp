#include <memory>
#include <string>
#include <fstream>
#include <yaml-cpp/yaml.h>

#include "ament_index_cpp/get_package_share_directory.hpp"
#include "geometry_msgs/msg/pose_stamped.hpp"
#include "rclcpp/rclcpp.hpp"
#include "std_srvs/srv/trigger.hpp"

#include "tf2_ros/transform_listener.h"
#include "tf2_ros/buffer.h"
#include "geometry_msgs/msg/transform_stamped.hpp"

/*
This node contains hande for two servies:
1. Save current pose im map frame into file.
call:    ros2 service call /save_approach_dock_pose std_srvs/srv/Trigger "{}"
2. Load data from that file and send it to nav2 as goal.
call:    ros2 service call /send_approach_dock_pose std_srvs/srv/Trigger "{}"
*/

class DockPoseManager : public rclcpp::Node
{
public:
  DockPoseManager() : Node("dock_approach_manager"), tf_buffer_(this->get_clock()), tf_listener_(tf_buffer_)
  {
    // Publisher
    this->goal_pub_ = this->create_publisher<geometry_msgs::msg::PoseStamped>("/goal_pose", 10);

    // Service handles
    this->save_srv_ = this->create_service<std_srvs::srv::Trigger>(
      "save_approach_dock_pose",
      std::bind(&DockPoseManager::handle_save, this, std::placeholders::_1, std::placeholders::_2)
    );
    this->send_srv_ = this->create_service<std_srvs::srv::Trigger>(
      "send_approach_dock_pose",
      std::bind(&DockPoseManager::handle_send, this, std::placeholders::_1, std::placeholders::_2)
    );

    // Pose file path
    std::string package_share_dir = ament_index_cpp::get_package_share_directory("firo_navigation");
    this->filename_ = package_share_dir + "/config/dock_approach_pose.yaml";

    RCLCPP_INFO(this->get_logger(), "Dock_Approach_Pose_Manager node ready. Services: /save_approach_dock_pose, /send_approach_dock_pose");
  }

private:
  void handle_save(const std::shared_ptr<std_srvs::srv::Trigger::Request> request, std::shared_ptr<std_srvs::srv::Trigger::Response> response)
  {
    (void)request;
    try {
        // Get current pose in map
        geometry_msgs::msg::TransformStamped tf = this->tf_buffer_.lookupTransform("map", "base_link", tf2::TimePointZero);
        YAML::Node data;
        data["position"]["x"] = tf.transform.translation.x;
        data["position"]["y"] = tf.transform.translation.y;
        data["position"]["z"] = tf.transform.translation.z;
        data["orientation"]["x"] = tf.transform.rotation.x;
        data["orientation"]["y"] = tf.transform.rotation.y;
        data["orientation"]["z"] = tf.transform.rotation.z;
        data["orientation"]["w"] = tf.transform.rotation.w;
        // Save pose into file
        std::ofstream fout(this->filename_);
        fout << data;
        fout.close();
        // Send return info
        response->success = true;
        response->message = "Dock approach pose saved to " + this->filename_;
        RCLCPP_INFO(this->get_logger(), "%s", response->message.c_str());
    // When tf error
    } catch (const tf2::TransformException & ex) {
        response->success = false;
        response->message = std::string("TF error: ") + ex.what();
        RCLCPP_ERROR(this->get_logger(), "%s", response->message.c_str());
    }
  }

  void handle_send(const std::shared_ptr<std_srvs::srv::Trigger::Request> request, std::shared_ptr<std_srvs::srv::Trigger::Response> response)
  {
    (void)request;
    try {
        // Load data from file
        YAML::Node node = YAML::LoadFile(this->filename_);
        // Send on topic
        geometry_msgs::msg::PoseStamped goal;
        goal.header.frame_id = "map";
        goal.header.stamp = this->now();
        goal.pose.position.x = node["position"]["x"].as<double>();
        goal.pose.position.y = node["position"]["y"].as<double>();
        goal.pose.position.z = node["position"]["z"].as<double>();
        goal.pose.orientation.x = node["orientation"]["x"].as<double>();
        goal.pose.orientation.y = node["orientation"]["y"].as<double>();
        goal.pose.orientation.z = node["orientation"]["z"].as<double>();
        goal.pose.orientation.w = node["orientation"]["w"].as<double>();
        this->goal_pub_->publish(goal);
        // Send response
        response->success = true;
        response->message = "Dock approach pose loaded and published to /goal_pose";
        RCLCPP_INFO(this->get_logger(), "%s", response->message.c_str());
    // When yaml error
    } catch (const std::exception & e) {
        response->success = false;
        response->message = std::string("YAML error: ") + e.what();
        RCLCPP_ERROR(this->get_logger(), "%s", response->message.c_str());
    }
  }
  
    // Params 
    std::string filename_;
    rclcpp::Publisher<geometry_msgs::msg::PoseStamped>::SharedPtr goal_pub_;
    rclcpp::Service<std_srvs::srv::Trigger>::SharedPtr save_srv_;
    rclcpp::Service<std_srvs::srv::Trigger>::SharedPtr send_srv_;
    tf2_ros::Buffer tf_buffer_;
    tf2_ros::TransformListener tf_listener_;
};

int main(int argc, char * argv[])
{
    rclcpp::init(argc, argv);
    auto node = std::make_shared<DockPoseManager>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}
