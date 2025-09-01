#include <memory>
#include <string>
#include <vector>

#include "geometry_msgs/msg/twist.hpp"
#include "geometry_msgs/msg/twist_stamped.hpp"
#include "action_msgs/msg/goal_status_array.hpp"
#include "rclcpp/rclcpp.hpp"

/*
This node converts Twist message given by navitaion2 stack into TwistStamped format. Out drivers require TwistSamped but 
nav2 on humble publishes Twist (changed in never nav2 verions). Due to this mechanism to stop robot aftear reching goal is added, as this
node would publish lastly recevied message over and over, which would case robot to still move after reaching goal (nav2 doesnt 'stop' the robot,
it only stops publishing messages)
*/

class CommandFixed : public rclcpp::Node
{
public:
  CommandFixed() : Node("command_fixer")
  {
    // Params delcaration
    frame_id = "navigation";

    goal_reached = false;

    // Subscribers
    subscriber_cmd_ = this->create_subscription<geometry_msgs::msg::Twist>(
      "/cmd_vel_nav_smoothed", 10, std::bind(&CommandFixed::CmdCallback, this, std::placeholders::_1));

    subscriber_goal_ = this->create_subscription<action_msgs::msg::GoalStatusArray>(
      "/navigate_to_pose/_action/status", 10, std::bind(&CommandFixed::GoalCallback, this, std::placeholders::_1));

    // Publisher
    publisher_cmd_ = this->create_publisher<geometry_msgs::msg::TwistStamped>("/cmd_vel", 10);
  }

private:
  void CmdCallback(const geometry_msgs::msg::Twist & msg)
  {
    // Create twist stamped message
    geometry_msgs::msg::TwistStamped msg_out;

    // Add stamp to message
    msg_out.header = std_msgs::msg::Header();
    msg_out.header.stamp = this->get_clock()->now();
    msg_out.header.frame_id = this->frame_id;
    msg_out.twist = msg;

    // Stop if goal is reached
    if (this->goal_reached)
    {
      msg_out.twist.linear.x = 0;
      msg_out.twist.angular.z = 0;

    }

    // Publish on output topic
    this->publisher_cmd_->publish(msg_out);
  }

  void GoalCallback(const action_msgs::msg::GoalStatusArray & msg)
  {
    // Check goal list
    if (!msg.status_list.empty()) {
      const auto &last_goal_status = msg.status_list.back();
      // Check goal reach status
      if (last_goal_status.status == 4)
      {
          this->goal_reached = true;
      }
      else 
      {
          this->goal_reached = false;
      }

    }
  }

  // Params 
  bool goal_reached;
  std::string frame_id;
  rclcpp::Subscription<geometry_msgs::msg::Twist>::SharedPtr subscriber_cmd_;
  rclcpp::Subscription<action_msgs::msg::GoalStatusArray>::SharedPtr subscriber_goal_;
  rclcpp::Publisher<geometry_msgs::msg::TwistStamped>::SharedPtr publisher_cmd_;
};

int main(int argc, char * argv[])
{
  rclcpp::init(argc, argv);
  auto node = std::make_shared<CommandFixed>();
  rclcpp::spin(node);
  rclcpp::shutdown();
  return 0;
}
