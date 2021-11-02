#!/usr/bin/env python3

import re
import os

# find the range of pod limit configs
# pod_name: aic-vdu-oam, aic-vdu-cprt, aic-vdu-up
def range_searcher(file_path, pod_name):
    with open(file_path) as f:
        linum = 0
        is_in_pod_config = 0
        for line in f:
            linum += 1
            #if(line == pod_name+':'):
            pattern = '^' + pod_name + ':'
            if(is_in_pod_config== 1 and line[0]!=' ' and line[0]!= '#' and len(line) > 2):
                pod_config_end = linum-1
                break
            if(re.match(pattern, line)):
                pod_config_start = linum
                is_in_pod_config = 1
    return (pod_config_start, pod_config_end)

def new_override_gen(file_path, config_range, pod_name):
    pod_config_start = config_range[0]
    pod_config_end= config_range[1]
    command_delete = "sed '{pod_config_start}d' {file_path} > /tmp/values-override-{pod_name}.yaml" \
        .format(pod_config_start = pod_config_start, file_path = file_path, pod_name = pod_name)
    command_indent = "sed -i '{pod_config_start},{pod_config_end}s/^[ ][ ]//' /tmp/values-override-{pod_name}.yaml" \
        .format(pod_config_start = pod_config_start+1, pod_config_end = pod_config_end-1, pod_name = pod_name)
    os.system(command_delete)
    os.system(command_indent)


    '''
if __name__=="__main__":
    file_path = '/home/diphia/temp/518_coverage/aic-dep/aic-dep-vdu/chart/aic-vdu/values-override.yaml'
    pod_config_range = range_searcher(file_path, 'aic-vdu-cprt')
    new_override_gen(file_path, pod_config_range, 'aic-vdu-cprt')
'''
