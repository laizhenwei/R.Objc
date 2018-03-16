# -*- coding: utf-8 -*-

import os
import sys
import re


# prefix
PREFIX = 'R'


# ignore paths
IGNORE_PATHS = []


# top comment
AUTHOR_COMMENT = '''//  Copyright 2018 laizw
//
//  Automatically Generated Files
//
//  Created by R.Objc
//

'''


# support types
SUPPORT_TYPES = {
    'Xib': {
        'exts': ['xib', 'nib'],
        'parser': {
            'defs': '- (UINib *){0};',
            'impl': '- (UINib *){0} {{\n\treturn [UINib nibWithNibName:@"{1}" bundle:nil];\n}}',
        }
    },
    'Storyboard': {
        'exts': ['storyboard'],
        'parser': {
            'defs': '- (UIStoryboard *){0};',
            'impl': '- (UIStoryboard *){0} {{\n\treturn [UIStoryboard storyboardWithName:@"{1}" bundle:nil];\n}}',
        }
    },
    'Image': {
        'exts': ['imageset'],
        'parser': {
            'defs': '- (UIImage *){0};',
            'impl': '- (UIImage *){0} {{\n\treturn [UIImage imageNamed:@"{1}"];\n}}',
        }
    },
    # 'Font': {
    #     'exts': ['ttf', 'otf'],
    #     'parser': {
    #         'defs': '- (UIFont *(^)(CGFloat)){0};',
    #         'impl': '- (UIFont *(^)(CGFloat)){0} {{\n\treturn ^(CGFloat size){{\n\t\treturn [UIFont fontWithName:@"{1}" size:size];\n\t}};\n}}',
    #     },
    # }
}

# support types extensions
SUPPORT_EXTS = {}
for key in SUPPORT_TYPES.keys():
    for ext in SUPPORT_TYPES[key]['exts']:
        SUPPORT_EXTS[ext] = key

print(SUPPORT_EXTS)

# R.h
R_H_TEMPLATE = AUTHOR_COMMENT + '''
{0}

@interface R : NSObject

{1}
@end
'''


# R.m
R_M_TEMPLATE = AUTHOR_COMMENT + '''
#import "R.h"

@implementation R

{0}
@end
'''


# XXX.h
R_RES_H_TEMPLATE = AUTHOR_COMMENT + '''
#import <Foundation/Foundation.h>
#import <UIKit/UIKit.h>

@interface {0} : NSObject

{1}
@end
'''


# XXX.m
R_RES_M_TEMPLATE = AUTHOR_COMMENT + '''
#import "{0}.h"

@implementation {0}

{1}
@end
'''

R_RES_PUBLIC_TEMPLATE = '''

'''


def findAllResource(dir, ret={}):
    dirs = os.listdir(dir)
    for file_name in dirs:
        if file_name in IGNORE_PATHS:
            continue

        filepath = os.path.join(dir, file_name)

        name, ext = os.path.splitext(file_name)
        ext = ext[1:]
        if ext in SUPPORT_EXTS.keys():
            res_type = SUPPORT_EXTS[ext]
            if res_type not in ret:
                ret[res_type] = []
            ret[res_type].append(name)
        elif os.path.isdir(filepath):
            findAllResource(filepath, ret)
    return ret


def generate_R_file(path):
    headers = ''
    properties = ''
    class_methods = ''
    for R_res_type in SUPPORT_TYPES.keys():
        R_file_name = PREFIX + R_res_type

        headers += '#import "{}.h"\n'.format(R_file_name)
        properties += '@property (class, readonly) {0} *{1};\n'.format(R_file_name, R_res_type)
        class_methods += '+ ({0} *){1} {{\n    static id impl = nil;\n    return impl = impl ?: [{0} new];\n}}\n'.format(R_file_name, R_res_type)

    # R.h
    R_h = open(path + 'R.h', 'wt')
    R_h.write(R_H_TEMPLATE.format(headers, properties))
    R_h.close()

    # R.m
    R_m = open(path + 'R.m', 'wt')
    R_m.write(R_M_TEMPLATE.format(class_methods))
    R_m.close()


def generate_R_RES_file(path, res):
    for (R_res_type, res_type_info) in SUPPORT_TYPES.items():
        R_file_name = PREFIX + R_res_type

        defs = ''
        impl = ''

        if R_res_type in res:
            files = res[R_res_type]

            parser = res_type_info['parser']
            if 'func' in parser:
                parser_func = parser['func']
                parser_func(files)
                continue

            for name in files:
                method = re.sub('[^a-zA-Z0-9_]', '_', name)
                defs += parser['defs'].format(method)
                defs += '\n'
                impl += parser['impl'].format(method, name)
                impl += '\n'

        # R_file_h
        R_file_h = open(path + R_file_name + '.h', 'wt')
        R_file_h.write(R_RES_H_TEMPLATE.format(R_file_name, defs))
        R_file_h.close()

        # R_file_m
        R_file_impl_m = open(path + R_file_name + '.m', 'wt')
        R_file_impl_m.write(R_RES_M_TEMPLATE.format(R_file_name, impl))
        R_file_impl_m.close()


def buildRFiles(path):
    all_res = findAllResource(path)
    if len(all_res) > 0:
        R_Objc_path = path + '/R.Objc/'
        if not os.path.exists(R_Objc_path):
            os.mkdir(R_Objc_path)

    generate_R_file(R_Objc_path)
    generate_R_RES_file(R_Objc_path, all_res)


buildRFiles(sys.argv[1])


