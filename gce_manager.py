#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
gce-manager: Google Compute Engine Manager
"""

from __future__ import print_function
import os
import sys
import datetime

__prog__ = os.path.basename(__file__)
__description__ = __doc__
__author__ = "Michiru Kaneda"
__copyright__ = "Copyright (c) 2018 Michiru Kaneda"
__credits__ = ["Michiru Kaneda"]
__license__ = "MIT"
__version__ = "v0.0.1"
__date__ = "04/Jun/2018"
__maintainer__ = "Michiru Kaneda"
__email__ = "Michiru.Kaneda@cern.ch"
__status__ = "Prototype"

from google.oauth2 import service_account
from apiclient.discovery import build

PARAMS = {
    "service_account_file":
    "",
    "project": "",
    "zone": "",
    "instance": "",
    "scopes": ["https://www.googleapis.com/auth/compute"],
    "config_file": os.environ["HOME"] + "/.config/gce-manager/config",
    "verbose": 2,
}

COLORS = {"black": "30", "red": "31", "green": "32", "yellow": "33",
          "blue": "34", "magenta": "35", "lightblue": 36, "white": 37}

def out(text, verbose=100, color="", is_date=True):
    """Print wrapper"""
    if PARAMS["verbose"] < verbose:
        return
    pre = post = ""
    if color != "" and sys.stdout.isatty():
        if color in COLORS.keys():
            pre = "\033[" + COLORS[color] + ";1m"
            post = "\033[m"
    if is_date:
        pre = "[" + datetime.datetime.today().strftime("%Y-%m-%d %X") +\
            "] " + pre
    print(pre + text + post)

def debug(text, verbose=3):
    """Debug level output"""
    out("[DEBUG]" + text, verbose)

def info(text, verbose=2):
    """Information level output"""
    out("[INFO]" + text, verbose)

def warn(text, verbose=1):
    """Warning level output"""
    out("[WARNING]" + text, verbose)

def err(text, verbose=0):
    """Error level output"""
    out("[ERROR]" + text, verbose)

def read_config():
    """Read configuration file."""
    if os.path.isfile(PARAMS["config_file"]):
        with open(PARAMS["config_file"]) as conf_file:
            for line in conf_file:
                line_orig = line
                if line.find("#") != -1:
                    line = line.split("#")[0].strip()
                if line == "":
                    continue
                if line.find("=") == -1 or len(line.split("=")) > 2:
                    warn("Wrong configuration line: " + line_orig)
                    continue
                (key, var) = line.split("=")
                PARAMS[key.strip()] = var.strip()

def build_compute():
    """Auth and Build"""
    credentials = service_account.Credentials.from_service_account_file(
        PARAMS["service_account_file"], scopes=PARAMS["scopes"])
    return build("compute", "v1", credentials=credentials)

def get_zones(compute, project):
    """Make zone list"""
    result = compute.zones().list(project=project).execute()
    return result["items"]

def print_zones(compute, project):
    """Print instances information"""
    import json
    mylist = get_zones(compute, project)
    if PARAMS["verbose"] > 2:
        print(json.dumps(mylist, indent=4, separators=(",", ": ")))
    else:
        for zone in mylist:
            print(zone["name"])

def get_instances(compute, project, zone):
    """Make instance list"""
    result = compute.instances().list(project=project, zone=zone).execute()
    return result["items"]

def print_instances(compute, project, zone):
    """Print instances information"""
    import json
    mylist = get_instances(compute, project, zone)
    if PARAMS["verbose"] > 2:
        print(json.dumps(mylist, indent=4, separators=(",", ": ")))
    else:
        for instance in mylist:
            print(instance["name"] + ": " + instance["status"])

def get_instance(compute, project, zone, instance):
    """Get each instance information"""
    result = compute.instances().get(project=project, zone=zone,
                                     instance=instance).execute()
    return result

def print_instance(compute, project, zone, instance):
    """Print each instance information"""
    import json
    myinstance = get_instance(compute, project, zone, instance)
    if PARAMS["verbose"] > 2:
        print(json.dumps(myinstance, indent=4, separators=(",", ": ")))
    else:
        ip = ""
        if "networkInterfaces" in myinstance:
            ni = myinstance["networkInterfaces"][0]
            if "accessConfigs" in ni:
                ac = ni["accessConfigs"][0]
                if "natIP" in ac:
                    ip = ", IP: " + ac["natIP"]

        print(myinstance["name"] + ", Status:" + myinstance["status"] + ip)

def start(compute, project, zone, instance):
    """Start instance"""
    import json
    result = compute.instances().start(project=project, zone=zone,
                                       instance=instance).execute()
    print(json.dumps(result, indent=4, separators=(",", ": ")))

def stop(compute, project, zone, instance):
    """Stop instance"""
    import json
    result = compute.instances().stop(project=project, zone=zone,
                                      instance=instance).execute()
    print(json.dumps(result, indent=4, separators=(",", ": ")))


def main():
    """Main function."""

    read_config()

    import argparse
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.RawTextHelpFormatter,
        description=__description__,
    )

    subparsers = parser.add_subparsers(
        title="subcommands", metavar="[command]", help="", dest="command")

    help_doc = "List up instances"
    subparsers.add_parser("instances", description=help_doc, help=help_doc,
                          formatter_class=argparse.RawTextHelpFormatter)
    help_doc = "List up zones"
    subparsers.add_parser("zones", description=help_doc, help=help_doc,
                          formatter_class=argparse.RawTextHelpFormatter)
    help_doc = "Start instance"
    subparsers.add_parser("start", description=help_doc, help=help_doc,
                          formatter_class=argparse.RawTextHelpFormatter)
    help_doc = "Stop instance"
    subparsers.add_parser("stop", description=help_doc, help=help_doc,
                          formatter_class=argparse.RawTextHelpFormatter)
    help_doc = "Get instance information"
    subparsers.add_parser("get", description=help_doc, help=help_doc,
                          formatter_class=argparse.RawTextHelpFormatter)
    help_doc = "or -h/--help\nPrint Help (this message)\n\n"
    subparsers.add_parser("help", description=help_doc, help=help_doc,
                          formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("-s", "--service_account_file",
                        action="store", default=PARAMS["service_account_file"],
                        help="Set service account file")
    parser.add_argument("-p", "--project",
                        action="store", default=PARAMS["project"],
                        help="Set project ID")
    parser.add_argument("-z", "--zone",
                        action="store", default=PARAMS["zone"],
                        help="Set zone")
    parser.add_argument("-i", "--instance",
                        action="store", default=PARAMS["instance"],
                        help="Set service account file")
    parser.add_argument("-v", "--verbose", type=int,
                        action="store", default=PARAMS["verbose"],
                        help="Verbose level"
                        " (0:error, 1: warning, 2: info, 3: debug)")
    parser.add_argument("-h", "--help",
                        action="store_true",
                        help="Print Help (this message)")

    args = parser.parse_args()

    if args.help or args.command == "help" or args.command == None:
        parser.print_help()
        sys.exit()

    need_service_account_file = ["instances", "zones", "start", "stop", "get"]
    need_project = ["instances", "zones", "start", "stop", "get"]
    need_zone = ["instances", "start", "stop", "get"]
    need_instance = ["start", "stop", "get"]

    for k, v in vars(args).items():
        PARAMS[k] = v

    if PARAMS["command"] in need_service_account_file and\
            PARAMS["service_account_file"] == "":
        err("Please set account service file")
        sys.exit(10)
    if PARAMS["command"] in need_project and PARAMS["project"] == "":
        err("Please set project ID")
        sys.exit(11)
    if PARAMS["command"] in need_zone and PARAMS["zone"] == "":
        err("Please set zone")
        sys.exit(12)
    if PARAMS["command"] in need_instance and PARAMS["instance"] == "":
        err("Please set instance")
        sys.exit(13)

    compute = build_compute()

    if PARAMS["command"] == "instances":
        print_instances(compute, PARAMS["project"], PARAMS["zone"])
    elif PARAMS["command"] == "zones":
        print_zones(compute, PARAMS["project"])
    elif PARAMS["command"] == "start":
        start(compute, PARAMS["project"], PARAMS["zone"],
                    PARAMS["instance"])
    elif PARAMS["command"] == "stop":
        stop(compute, PARAMS["project"], PARAMS["zone"],
                    PARAMS["instance"])
    elif PARAMS["command"] == "get":
        print_instance(compute, PARAMS["project"], PARAMS["zone"],
                     PARAMS["instance"])

if __name__ == "__main__":
    main()
