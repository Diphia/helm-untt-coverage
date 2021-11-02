#!/usr/bin/env python3

import yaml
import pickle

def template_extractor(template_file):
    template_file_path = '/tmp/' + template_file
    with open(template_file_path) as f:
        primitive_dict = yaml.safe_load(f)
    # get keys, and remove the '.' in the beginning of key
    #key_value_list = list(map(lambda key: (key[0][1:],key[1]), key_extract_handler(primitive_dict,'',[])))
    try:
        key_value_list = list(map(lambda key: (key[0][1:],key[1]), key_extract_handler(primitive_dict,'',[])))
    except:
        key_value_list = []
    return key_value_list

def key_extract_handler(current, path, result):
    if(type(current) == dict):
        for key in current:
            if(type(current[key]) == dict or type(current[key]) == list):
                key_extract_handler(current[key], path + '.' + key, result)
            else:
                result.append((path + '.' + key, current[key]))
        return result
    if(type(current) == list):
        for i in range(len(current)):
            if(type(current[i]) == dict or type(current[i]) == list):
                key_extract_handler(current[i], path + '[' + str(i) + ']', result)
            else:
                result.append((path + '[' + str(i) + ']', current[i]))
        return result

def ut_generator(key_value_list):
    ut_file = ''
    for key_value in key_value_list:
        if (key_value[1]!= True and key_value[1]!= False and key_value[1]!= 'true' and key_value[1]!= 'false' and key_value[1]!= 'FALSE' and key_value[1]!= 'TRUE'):
            current_key_value = '"{key_value}"'.format(key_value = key_value[1])
        else:
            current_key_value = key_value[1]
        case = '- equal:\n    path: {key}\n    value: {value}\n'\
            .format(key = key_value[0], value = current_key_value)
        ut_file += case
    print(ut_file)

if __name__=="__main__":
    #filelist = ['apigw-manager-service.yaml', 'apigw-service.yaml', 'certificate-service.yaml', 'common-configmap.yaml', 'dhcp-configmap.yaml', 'ipmgmt-service.yaml', 'ne3s-service.yaml', 'networkinit-configmap.yaml', 'nwmgmt-service.yaml', 'oamagent-publish-service.yaml', 'oam-asm-service.yaml', 'oam-cpconfig-service.yaml', 'oam-deployment.yaml', 'oam-fm-service.yaml', 'oam-ne3sagent-configmap.yaml', 'oam-pm-service.yaml', 'oam-trsconfig-service.yaml', 'providercontroller-service.yaml', 'pvc-apigw.yaml', 'route-init-configmap.yaml', 'rsyslog-config.yaml', 'secret.yaml']
    #filelist = ['common-configmap.yaml', 'cprt-deployment.yaml', 'networkinit-configmap.yaml', 'route-init-configmap.yaml', 'rsyslog-config.yaml']
    filelist = ['oamasm-service.yaml']
    for item in filelist:
        filename = item
        key_value_list = template_extractor(filename)
        test_filename = filename.split('.')[0] + '_test.yaml'
        dumped_file = '/tmp/key_list_{test_filename}.pickle'.format(test_filename = test_filename)
        try:
            with open(dumped_file, 'rb') as f:
                exist_case_list = pickle.load(f)
            key_value_list = filter(lambda item: item not in exist_case_list, key_value_list)
        except:
            pass
        ut_generator(key_value_list)
