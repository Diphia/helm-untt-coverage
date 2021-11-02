#!/usr/bin/env python3

from coverage_exec import *
from override_process import *

if __name__=="__main__":
    try:
        chart_path = os.path.abspath(sys.argv[1]) + '/'
    except:
        print('No Chart Path Specified')
        print('Usage: untt-coverage <CHART_PATH>')
        exit()

    to_override_list = ['aic-vdu-up', 'aic-vdu-cprt', 'aic-vdu-oam']
    pod_name = chart_path.split('/')[-2]
    if (pod_name in to_override_list):
        override_file_path = '/home/diphia/temp/629_ut/aic-dep/aic-dep-vdu/chart/aic-vdu/values-override.yaml'
        pod_config_range = range_searcher(override_file_path, pod_name)
        new_override_gen(override_file_path, pod_config_range, pod_name)

    template_path = chart_path + 'templates/'
    test_path = chart_path + 'tests/'
    template_files= list(filter(lambda filename: filename[-5:]=='.yaml', \
                                os.listdir(template_path)))
    helm_render(chart_path, template_files, pod_name)
    chart_result = comparison(template_files, test_path)
    full_log = log_generator(chart_result)
    with open('/tmp/log', 'w') as f:
        f.write(full_log)
    terminal_output = terminal_output_generator(chart_result)
    print(terminal_output)
    report_generator(chart_result)
