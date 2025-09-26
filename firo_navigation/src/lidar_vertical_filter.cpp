#include <cmath>
#include <limits>
#include <memory>
#include <sensor_msgs/msg/laser_scan.hpp>
#include "rclcpp/rclcpp.hpp"
/*
This node filters scans from the vertical lidars in order to detect obstalce height that is lower than mast (threshold).

sensor_msgs/msg/LaserScan.msg:
std_msgs/msg/Header header
float angle_min
float angle_max
float angle_increment
float time_increment
float scan_time
float range_min
float range_max
float[] ranges
float[] intensities
*/
constexpr double PI = 3.14159265358979323846;
class VerticalFilter : public rclcpp::Node
{
public:
  VerticalFilter() : Node("lidar_vertical_filter")
  {
    // Params
    this->height_threshold = 1.5;

    // Subscribers
    this->subscriber_left_ = this->create_subscription<sensor_msgs::msg::LaserScan>(
      "lidar_vertical_left/scan", 10,
      std::bind(&VerticalFilter::LeftCallback, this, std::placeholders::_1));
    this->subscriber_right_ = this->create_subscription<sensor_msgs::msg::LaserScan>(
      "lidar_vertical_right/scan", 10,
      std::bind(&VerticalFilter::RightCallback, this, std::placeholders::_1));

    // Publishers
    this->publisher_left_ = this->create_publisher<sensor_msgs::msg::LaserScan>(
      "/lidar_vertical_left/scan_filtered", 10);
    this->publisher_right_ = this->create_publisher<sensor_msgs::msg::LaserScan>(
      "/lidar_vertical_right/scan_filtered", 10);
  }

private:
  void RightCallback(const sensor_msgs::msg::LaserScan & msg)
  {
    // Copy message
    sensor_msgs::msg::LaserScan msg_out = msg;

    // Filter scans
    float current_angle = msg_out.angle_min;
    for (size_t i = 0; i < msg_out.ranges.size(); i++) {
      if (!std::isnan(msg_out.ranges[i])) {
        // front of robot
        if (current_angle < 0.5*PI) {
          // if above treshold then set as nan
          if (msg_out.ranges[i] * std::sin(current_angle) >= this->height_threshold) {
            msg_out.ranges[i] = std::numeric_limits<float>::quiet_NaN();
          }
        }
        // above of robot
        else if (current_angle == 0.5*PI) {
          // if above treshold then set as nan
          if (msg_out.ranges[i] >= this->height_threshold) {
            msg_out.ranges[i] = std::numeric_limits<float>::quiet_NaN();
          }
        }
        // behind of robot
        else if ( (current_angle > 0.5*PI) && (current_angle < PI) ) {
          // if above treshold then set as nan
          if (msg_out.ranges[i] * std::sin(PI - current_angle) >= this->height_threshold) {
            msg_out.ranges[i] = std::numeric_limits<float>::quiet_NaN();
          }
        }
      }
      current_angle += msg_out.angle_increment;
    }

    // Publish on output topic
    this->publisher_right_->publish(msg_out);
  }
  void LeftCallback(const sensor_msgs::msg::LaserScan & msg)
  {
    // Copy message
    sensor_msgs::msg::LaserScan msg_out = msg;

    // Filter scans
    float current_angle = msg_out.angle_min;

    for (size_t i = 0; i < msg_out.ranges.size(); i++) {
      if (!std::isnan(msg_out.ranges[i])) {
        // front of robot
        if (current_angle > 1.5*PI) {
          // if above treshold then set as nan
          if (msg_out.ranges[i] * std::sin(2.0*PI - current_angle) >= this->height_threshold) {
            msg_out.ranges[i] = std::numeric_limits<float>::quiet_NaN();
          }
        }
        // above of robot
        else if (current_angle == 1.5*PI) {
          // if above treshold then set as nan
          if (msg_out.ranges[i] >= this->height_threshold) {
            msg_out.ranges[i] = std::numeric_limits<float>::quiet_NaN();
          }
        }
        // behind of robot
        else if ( (current_angle > PI) && (current_angle < 1.5*PI) ) {
          // if above treshold then set as nan
          if (msg_out.ranges[i] * std::sin(current_angle - PI) >= this->height_threshold) {
            msg_out.ranges[i] = std::numeric_limits<float>::quiet_NaN();
          }
        }
      }
      current_angle += msg_out.angle_increment;
    }

    // Publish on output topic
    this->publisher_left_->publish(msg_out);
  }

  // Params
  float height_threshold;
  rclcpp::Subscription<sensor_msgs::msg::LaserScan>::SharedPtr subscriber_left_;
  rclcpp::Subscription<sensor_msgs::msg::LaserScan>::SharedPtr subscriber_right_;
  rclcpp::Publisher<sensor_msgs::msg::LaserScan>::SharedPtr publisher_left_;
  rclcpp::Publisher<sensor_msgs::msg::LaserScan>::SharedPtr publisher_right_;
};

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  auto node = std::make_shared<VerticalFilter>();
  rclcpp::spin(node);
  rclcpp::shutdown();
  return 0;
}
