#!/usr/bin/env python
# encoding: utf8

import rospy
from rico_context.msg import HistoryEvent
from rico_context.srv import GetContext, GetContextResponse, ResetContext, ResetContextResponse, IsInTask, IsInTaskResponse, GetCurrentScenarioId, GetCurrentScenarioIdResponse

class RicoContext(object):
    def __init__(self):
        self.history = []

        self.sub = rospy.Subscriber('/context/push', HistoryEvent, self.push_callback)
        self.get_service = rospy.Service('/context/get', GetContext, self.get_context)
        self.reset_service = rospy.Service('/context/reset', ResetContext, self.reset_context)
        self.is_in_task_service = rospy.Service('/context/is_in_task', IsInTask, self.is_in_task)
        self.get_current_scenario_id_service = rospy.Service('/context/scenario_id', GetCurrentScenarioId, self.get_current_scenario_id)


    def push_callback(self, msg):
        is_idle = 'idle' in msg.complement

        if not is_idle:
            self.history.append(msg)
        rospy.loginfo("History: %s", self.history)

    def get_context(self, req):
        rospy.loginfo("Get context: %s", req)
        return GetContextResponse(self.history)
    
    def is_in_task(self, req):
        is_in_task = False

        for event in self.history:
            if event.actor == 'system' and event.action == 'trigger scenario':
                is_in_task = True
            elif event.actor == 'system' and event.action == 'finish scenario':
                is_in_task = False
            elif event.action == 'start performing' and 'idle' not in event.complement:
                is_in_task = True
            elif event.action == 'finish performing':
                is_in_task = False

        return IsInTaskResponse(is_in_task)
    
    def get_current_scenario_id(self, req):
        curr_scenario_id = None

        for event in self.history:
            if event.actor == 'system' and event.action == 'trigger scenario':
                curr_scenario_id = int(event.complement)

        return GetCurrentScenarioIdResponse(curr_scenario_id)
    
    def reset_context(self, req):
        rospy.loginfo("Reset context: %s", req)
        success = False

        try:
            self.history = []
            success = True
        except Exception as e:
            rospy.logerr("Error resetting context: %s", e)

        return ResetContextResponse(success)

def main():
    rospy.init_node('rico_context', anonymous=True)
    rospy.loginfo("rico_context node started")
    RicoContext()
    rospy.spin()

if __name__ == '__main__':
    main()
