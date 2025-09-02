#include <memory>
#include <string>
#include <vector>

#include "nav_msgs/msg/odometry.hpp"
#include "rclcpp/rclcpp.hpp"

/*
Rf2o odometry node doesn't provide covariance matrix which needs to be added. Can be given with yaml file.
Also, rf2o gives linear velocity in opposite direction. For now, this can't be addressed as lidar driver node does 
not allow for snipping scans from the front. Angular velocity is correct sign.

This node publishes fixed odometry message from given topic only after original is published. 
Inputs:
 odom_topic - topic which message will be fixed
 odom_topic_fixed - topic on wich fixed message is published
 covariance - given covariance matrix
 coeff_x - parameter to scale/change v_x
 coeff_yaw - parameter to scale/change yaw rate
Outputs:
  message from odom_topic is published onto odom_topic_fixed with gioven covaraince and changed v_x direction -> see OdomCallback function.
*/

class OdometryFixer : public rclcpp::Node
{
public:
  OdometryFixer() : Node("covariance_fixer")
  {
    // Params delcaration

    // Topic names
    this->declare_parameter<std::string>("odom_topic", "/odom_lidar_rf");
    this->get_parameter("odom_topic", this->input_topic_);
    this->declare_parameter<std::string>("odom_topic_fixed", "/odom_lidar_rf_fixed");
    this->get_parameter("odom_topic_fixed", this->output_topic_);


    // Initial covarance matrix
    std::vector<double> param_cov;
    this->declare_parameter<std::vector<double>>(
      "covariance", {0.1, 0.0, 0.0,    0.0, 0.0,    0.0, 0.0, 0.1, 0.0, 0.0,    0.0, 0.0,
                     0.0, 0.0, 9999.0, 0.0, 0.0,    0.0, 0.0, 0.0, 0.0, 9999.0, 0.0, 0.0,
                     0.0, 0.0, 0.0,    0.0, 9999.0, 0.0, 0.0, 0.0, 0.0, 0.0,    0.0, 0.1});
    this->get_parameter("covariance", param_cov);
    // Check matrix size
    if (param_cov.size() != 36) {
      RCLCPP_ERROR(this->get_logger(), "Covariance must have 36 elements!");
      rclcpp::shutdown();
      return;
    }
    // Copy to array
    std::copy(param_cov.begin(), param_cov.end(), default_covariance_.begin());

    // Modify values params
    this->declare_parameter<double>("x_dot_coeff", 1.0);
    this->get_parameter("x_dot_coeff", this->coeff_x_);
    this->declare_parameter<double>("yaw_dot_coeff", 1.0);
    this->get_parameter("yaw_dot_coeff", this->coeff_yaw_);

    // Subscriber
    this->subscriber_ = this->create_subscription<nav_msgs::msg::Odometry>(
      this->input_topic_, 10, std::bind(&OdometryFixer::OdomCallback, this, std::placeholders::_1));
    // Publisher
    this->publisher_ = this->create_publisher<nav_msgs::msg::Odometry>(this->output_topic_, 10);
  }

private:
  void OdomCallback(const nav_msgs::msg::Odometry & msg)
  {
    // Copy message
    nav_msgs::msg::Odometry msg_out = msg;

    // Modify new message
    msg_out.twist.twist.linear.x = this->coeff_x_*msg.twist.twist.linear.x; // fix v_x sign
    msg_out.twist.twist.angular.z = this->coeff_yaw_*msg.twist.twist.angular.z; // fix yaw_vel sign
    msg_out.twist.covariance = default_covariance_; // set given covariance

    // Publish on output topic
    this->publisher_->publish(msg_out);
  }

  // Params 
  std::string input_topic_;
  std::string output_topic_;
  std::array<double, 36> default_covariance_{};
  double coeff_x_;
  double coeff_yaw_;
  rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr subscriber_;
  rclcpp::Publisher<nav_msgs::msg::Odometry>::SharedPtr publisher_;
};

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  auto node = std::make_shared<OdometryFixer>();
  rclcpp::spin(node);
  rclcpp::shutdown();
  return 0;
}
