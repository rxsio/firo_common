#include <memory>
#include <string>
#include <vector>

#include "nav_msgs/msg/odometry.hpp"
#include "rclcpp/rclcpp.hpp"

class CovarianceFixer : public rclcpp::Node
{
public:
  CovarianceFixer() : Node("covariance_fixer")
  {
    // Params delcaration
    // Topic names
    this->declare_parameter<std::string>("odom_topic", "/odom_lidar_rf");
    std::string input_topic = this->get_parameter("odom_topic").as_string();
    this->declare_parameter<std::string>("odom_topic_fixed", "/odom_lidar_rf_fixed");
    std::string output_topic = this->get_parameter("odom_topic_fixed").as_string();
    std::vector<double> param_cov;
    // Covarance matrix
    this->declare_parameter<std::vector<double>>(
      "covariance", {0.1, 0.0, 0.0,    0.0, 0.0,    0.0, 0.0, 0.1, 0.0, 0.0,    0.0, 0.0,
                     0.0, 0.0, 9999.0, 0.0, 0.0,    0.0, 0.0, 0.0, 0.0, 9999.0, 0.0, 0.0,
                     0.0, 0.0, 0.0,    0.0, 9999.0, 0.0, 0.0, 0.0, 0.0, 0.0,    0.0, 0.1});
    this->get_parameter("covariance", param_cov);
    // Check size
    if (param_cov.size() != 36) {
      RCLCPP_ERROR(this->get_logger(), "Covariance must have 36 elements!");
      rclcpp::shutdown();
      return;
    }
    // Copy to array
    std::copy(param_cov.begin(), param_cov.end(), default_covariance_.begin());

    // Subscriber
    subscription_ = this->create_subscription<nav_msgs::msg::Odometry>(
      input_topic, 10, std::bind(&CovarianceFixer::OdomCallback, this, std::placeholders::_1));

    // Publisher
    publisher_ = this->create_publisher<nav_msgs::msg::Odometry>(output_topic, 10);
  }

private:
  void OdomCallback(const nav_msgs::msg::Odometry & msg)
  {
    // Copy message
    nav_msgs::msg::Odometry msg_out = msg;

    // Modify new message
    msg_out.twist.covariance = default_covariance_;

    // Publish on output topic
    publisher_->publish(msg_out);
  }

  std::array<double, 36> default_covariance_{};
  rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr subscription_;
  rclcpp::Publisher<nav_msgs::msg::Odometry>::SharedPtr publisher_;
};

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  auto node = std::make_shared<CovarianceFixer>();
  rclcpp::spin(node);
  rclcpp::shutdown();
  return 0;
}
