__author__ = "Richard O'Dwyer"
__email__ = "richard@richard.do"
__license__ = "None"

import re
import socket
import operator
import sys,getopt
import pprint
import os,glob
import argparse
from collections import OrderedDict
import csv

parser = argparse.ArgumentParser()
parser.add_argument("log", help="the log file or directory you wish to parse")
parser.add_argument("-t", help="only print out the top t amount of results", type=int)
parser.add_argument("-c", help="Use this flag to output the parse to a csv file", action="store_true")
args = parser.parse_args()
pp = pprint.PrettyPrinter(indent=4)

def process_log(log):
    requests = get_requests(log)
    ips = get_ipaddress(requests)
    totals = item_occur(ips)
    if args.t:
        totals = crop_results(totals, args.t)
    logs = get_hostnames(totals)
    return logs

def get_hostnames(ipdict):
    logs = []
    for log in ipdict:
        d = {}
        d['ip'] = log
        try:
            d['hostname'] = socket.gethostbyaddr(log)[0]
        except socket.herror:
            d['hostname'] = "Could not find hostname" 
        d['count'] = ipdict[log]
        logs.append(d)
    logs.sort(key=operator.itemgetter('count'))
    logs.reverse()
    return logs

def crop_results(totals, amount):
    sort = OrderedDict(sorted(totals.items(), key=lambda t: t[1]))#order them
    ret = {}
    if len(sort) > amount: #make sure we don't index out of bounds
        ret.update(sort.items()[-amount:])#cast to list. retrieve last 'amount' number of items and add to dictionary
        return ret

    return sort

def get_requests(log_line):
    pat = (r''
           '(\d+.\d+.\d+.\d+)\s-\s-\s' #IP address
           '\[(.+)\]\s' #datetime
           '"GET\s(.+)\s\w+/.+"\s\d+\s' #requested file
           '\d+\s"(.+)"\s' #referrer
           '"(.+)"' #user agent
        )
    requests = find(pat, log_line, None)
    return requests

def find(pat, text, match_item):
    match = re.findall(pat, text)
    if match:
        return match
    else:
        return False

def get_ipaddress(requests):
    return get_info(requests, info = 'ipaddress')
def get_datetime(requests):
    return get_info(requests, info = 'datetime')
def get_request(requests):
    return get_info(requests, info = 'request')
def get_referrer(requests):
    return get_info(requests, info = 'referrer')
def get_useragent(requests):
    return get_info(requests, info = 'useragent')

def get_info(requests, info):
    keys = ['ipaddress','datetime','request','referrer','useragent']
    requested_info = []
    for req in requests:
        dictionary = dict(zip(keys, req))
        requested_info.append(dictionary[info])
    return requested_info

def item_occur(lines):
    #the lines parameter is a list.
    #This function returns a dict where there is a key for each unique item in the list
    #and the value is the amount of times that item appears in the list
    
    d = {}
    for item in lines:
        d[item] = d.get(item,0)+1
    return d

def output(logs):
    keys = ['ip', 'hostname', 'count']
    with open('Nginx_log_parser_output.csv', 'wb') as f:
        dict_writer = csv.DictWriter(f, keys)
        dict_writer.writer.writerow(keys)
        dict_writer.writerows(logs)
    
if __name__ == '__main__':
    inputfile =''
    
    if args.log:
        if os.path.isdir(args.log):
            input_filenames = os.listdir(args.log)
            log_file =''
            for file in input_filenames:
                log_file += open(args.log+'/'+file, 'r').read()

        elif os.path.isfile(args.log):
            log_file = open(args.log, 'r').read()
        #else:
            #watdo?
    else:    
        #sample output
        log_file = open('example.log', 'r')

    if args.c!=0:    
        output(process_log(log_file))
    else:
        pp.pprint(process_log(log_file))
    
