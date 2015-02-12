from planner.strategies.strategy import Strategy

__author__ = 'Sam and alex'


class Defender1(Strategy):

    def __init__(self, world, robot_tag, actual_robot):
        super(Defender1, self).__init__(world, robot_tag, actual_robot)

    def act(self):
        self.fetch_world_state()
        zone_ball = self.world.get_zone(self.ball.position)
        zone_robot = self.world.get_zone(self.robot.position)

        if zone_ball == zone_robot:
            print "ball is in robot's zone"
            if not ball_going_quickly():
                #ball is stationary, or essentially stationary
                if not self.is_ball_close():

                    if self.is_grabber_down: #raise the cage
                        self.raise_cage()

                    else:

                        if not self.is_robot_facing_ball():
                            print "robot is not facing ball"
                            to_turn =self.robot.angle_to_point(self.ball.position)
                            print "rotating robot to " + str(to_turn) + " radians"
                            self.actual_robot.turn(to_turn)

                        else: # we are facing the ball
                            print "robot is facing the ball"
                            if not self.is_ball_close:
                                print "Ball is far away"
                                dist_to_ball = self.dist_from_kicker_to_ball()
                                self.actual_robot.move_forward(dist_to_ball)

                else:  # the ball can be held
                    print "ball is close to robot kicker"
                    if self.is_grabber_down:  # we must be holding the ball
                        print "cage is down"
                        if not self.is_robot_facing_goal():  # are we facing the goal?
                            print "robot not facing goal"
                            to_turn = self.robot.angle_to_point(self.world.goal)
                            print "rotating robot " + str(to_turn) + " radians"
                            self.actual_robot.turn(to_turn)  # turn towards the the goal

                        else:  # we are facing the goal
                            print "robot is facing goal"
                            self.actual_robot.kick(power=1.0)  # kick

                    else:  # lower the cage
                        print "cage is up"
                        self.lower_cage()
            else: # The ball is going quickly. Block the ball.
            	if not self.sidewards:
            		robot_x = self.robot.x
            		set_point = (robot_x, 0)
            		to_turn = self.robot.angle_to_point(set_point)
            		print "rotating robot to " + str(to_turn) + " radians"
            		self.actual_robot.turn(to_turn) # turn towards the sideline
            	else:
            		x = self.robot.x
            		y = predict_y(self, x, ball)
            		dist_to_point = self.dist_from_robot_to_point(x,y)
            		print dist_to_point
            		self.actual_robot.move_forward(dist_to_point)
        else: #ball is not in our zone
            if not ball_going_quickly():
                # the below is not needed for this milestone as we can't move before the ball is kicked, but may come in useful in general play.
                """if not self.alligned(): #we are not in position
                    print "robot is not aligned"
                    to_turn = self.robot.angle_to_point(set_position) #need to define a set position in front of goal.
                    print "rotating robot to " + str(to_turn) + " radians"
                    self.actual_robot.turn(to_turn)
                    dist_to_pos = self.dist_from_kicker_to_pos() #need to define based on set position
                    print "moving robot " + str(dist_to_pos)
                    self.actual_robot.move_forward(dist_to_pos)
                else: #we are in the correct position
                    if not self.sidewards: #robot is not side on 
                        robot_x = self.robot.x
                        set_point = (robot_x, 0)
                        to_turn = self.robot.angle_to_point(set_point)
                        print = "rotating robot to " + str(to_turn) + " radians"
                        self.actual_robot.turn(to_turn)
                    else:
                    	pass #hold"""
                pass
            else:  #ball is going quickly, block the ball.
            	if not self.sidewards:
            		robot_x = self.robot.x
            		set_point = (robot_x, 0)
            		to_turn = self.robot.angle_to_point(set_point)
            		print "rotating robot to " + str(to_turn) + " radians"
            		self.actual_robot.turn(to_turn) # turn towards the sideline
            	else:
            		x = self.robot.x
            		y = predict_y(self, x, ball)
            		dist_to_point = self.dist_from_robot_to_point(x,y)
            		print dist_to_point
            		self.actual_robot.move_forward(dist_to_point)
