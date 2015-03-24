from vision_controller import VisionController
import time
vc = VisionController(video_port=None, draw_debug=('pos', 'vel', 'dir'))
state = None
t = 0
st = time.time()
while True:
    state = vc.analyse_frame(previous_state=state)
    # parse state into worldstate obj. See VC.draw_frame_details
    # pass worldstate to planner
    # done
    t += 1
    if t >= 72:
        print 72.0/(time.time() - st), "fps"
        try:
            print repr(state.get_robot(2).get_position_units())
        except Exception:
            pass
        t = 0
        st = time.time()
        
    
# todo:
# fix defender zone ranges
# distortion
# height compensation
# 
