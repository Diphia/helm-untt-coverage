#!/usr/bin/env python3

import yaml
import os, sys, subprocess
from termcolor import colored
from override_process import *
import re
import pickle

def helm_render(chart_path, template_files, pod_name):
    template_path = chart_path + 'templates/'
    for i in range(len(template_files)):
        #command = 'helm template -s templates/{template_file} {chart_path} -f {chart_path}values.yaml -f /tmp/aic-vdu-values.yaml -f /tmp/values-override-{pod_name}.yaml > /tmp/{template_file}' \
        command = 'helm template -s templates/{template_file} {chart_path} -f {chart_path}values.yaml -f {chart_path}tests/values/values_default.yaml > /tmp/{template_file}' \
            .format(template_file = template_files[i], chart_path = chart_path, pod_name = pod_name)
        print(command)
        render = subprocess.run(command, shell=True, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, universal_newlines=True)

def template_extractor(template_file):
    template_file_path = '/tmp/' + template_file
    with open(template_file_path) as f:
        primitive_dict = yaml.safe_load(f)
    # get keys, and remove the '.' in the beginning of key
    try:
        key_list = list(map(lambda key: key[1:], key_extract_handler(primitive_dict,'',[])))
    except:
        key_list = []
    return key_list


def key_extract_handler(current, path, result):
    if(type(current) == dict):
        for key in current:
            if(type(current[key]) == dict or type(current[key]) == list):
                key_extract_handler(current[key], path + '.' + key, result)
            else:
                result.append(path + '.' + key)
        return result
    if(type(current) == list):
        for i in range(len(current)):
            if(type(current[i]) == dict or type(current[i]) == list):
                key_extract_handler(current[i], path + '[' + str(i) + ']', result)
            else:
                result.append(path + '[' + str(i) + ']')
        return result

def test_extractor(test_path, test_file):
    test_file_path = test_path + test_file
    try:
        with open(test_file_path) as f:
            primitive_dict = yaml.safe_load(f)
        test_key_list = test_key_extract_handler(primitive_dict,[])
        dump_file = '/tmp/key_list_{test_file}.pickle'.format(test_file = test_file)
        with open(dump_file, 'wb') as f:
            pickle.dump(test_key_list, f)
        return test_key_list
    except:
        return []

def test_key_extract_handler(current, result):
    if(type(current) == dict):
        for key in current:
            if(type(current[key]) == dict or type(current[key]) == list):
                test_key_extract_handler(current[key], result)
            elif(key == 'path'):
                result.append(current[key])
        return result
    if(type(current) == list):
        for i in range(len(current)):
            if(type(current[i]) == dict or type(current[i]) == list):
                test_key_extract_handler(current[i], result)
        return result

def comparison(template_files, test_path):
    chart_result = []
    for template in template_files:
        test_file = template.split('.')[0] + '_test.yaml'
        key_list = template_extractor(template)
        test_key_list = test_extractor(test_path, test_file)
        key_count = 0
        #template_result = []
        if(test_key_list == None):
            continue
        for key in key_list:
            if(key in test_key_list):
                key_count += 1
                key_state = 1
            else:
                key_state = 0
            chart_result.append([key, key_state, template])
        #chart_result.append(template_result)
    return chart_result

def log_generator(chart_result):
    full_log = ''
    for item in chart_result:
        key_path = item[0]
        key_state = '[COVERED]' if item[1] == 1 else '[MISSING]'
        template_file = item[2]
        full_log += "{key_state}  {key_path}  {template_file} \n" \
            .format(key_path = key_path, \
                    key_state = key_state, \
                    template_file = template_file)
    return full_log

def terminal_output_generator(chart_result):
    output = ''
    total = len(chart_result)
    covered = len(list(filter(lambda row:row[1] == 1, chart_result)))
    try:
        output = \
            "Covered Keys: {covered}\n\
Total Keys: {total}\n\
Coverage: {coverage}%" \
            .format(total = total, covered = covered, coverage = round(covered/total*100, 2))
    except:
        output = \
            "Covered Keys: {covered}\n\
Total Keys: {total}\n\
Coverage: {coverage}%" \
            .format(total = total, covered = covered, coverage = 0)
    return output

def report_generator(chart_result):
    with open('./report/report_body.html', 'w') as f:
        for key_pair in chart_result:
            key_state = 'Covered' if key_pair[1] == 1 else 'Missing'
            block = '\t\t\t\t\t\t  <tr>\n\t\t\t\t\t\t    <th scope="row>{key_name}</th>\n\t\t\t\t\t\t    <td>{key_state}</td>\n\t\t\t\t\t\t    <td>{file_name}</td>\n\t\t\t\t\t\t  </tr>\n' \
                .format(key_name = key_pair[0], key_state = key_state, file_name=key_pair[2])
            f.write(block)
    command_merge_1 = 'cat ./report/index_template_head.html > ./report/report.html'
    command_merge_2 = 'cat ./report/report_body.html >> ./report/report.html'
    command_merge_3 = 'cat ./report/index_template_tail.html >> ./report/report.html'
    os.system(command_merge_1)
    os.system(command_merge_2)
    os.system(command_merge_3)
