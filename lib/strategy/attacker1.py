from generalized_strategy import generalized_strategy

__author__ = 'alex'


class attacker1(generalized_strategy):

    def __init__(self):
        pass

    def act(self):
        zone_ball = self.current_state.getZone(self.ball)


        if zone_ball == self.current_state.Zone.L_ATT: # is the ball in our zone?

            if (!we_have_ball): # do we have the ball?

                if (!we_are_facing_the_ball): # are we facing the ball?
                    # turn towards the the ball

                else: # we're not facing the ball

                    if(!we_are_close_to_ball): # are we close enough to the ball?
                        pass # keep moving

                    else: # we are close to the bal
                        pass # stop and lower cage

            else:# we have the ball

                if(!we_are_facing_the_goal): # are we facing the goal?
                    pass # turn towards the goal

                else:# we are facing the goal
                    pass #kick

        else: #the ball is not in our zone
            pass # hold
