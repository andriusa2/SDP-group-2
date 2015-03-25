from vision_controller import VisionController
import time
import sys
try:
    muh_id = sys.argv[-1]
    muh_id = int(muh_id)
except Exception:
    muh_id = 1
vc = VisionController(video_port=0, draw_debug=('pos', 'vel', 'dir'), id=muh_id)
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
