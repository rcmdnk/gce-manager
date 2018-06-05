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

class Output(object):
    """Print wrapper"""

    def __init__(self, verbose=2):
        self.colors = {"black": "30", "red": "31", "green": "32",
                       "yellow": "33", "blue": "34", "magenta": "35",
                       "lightblue": 36, "white": 37}
        self.verbose = verbose

    def set_verbose(self, verbose):
        """Set verbose level"""
        self.verbose = verbose

    def output(self, text, verbose=100, color="", is_date=True):
        """Print wrapper"""
        if self.verbose < verbose:
            return
        pre = post = ""
        if color != "" and sys.stdout.isatty():
            if color in self.colors:
                pre = "\033[" + self.colors[color] + ";1m"
                post = "\033[m"
        if is_date:
            pre = "[" + datetime.datetime.today().strftime("%Y-%m-%d %X") +\
                "] " + pre
        print(pre + text + post)

    def debug(self, text, verbose=3):
        """Debug level output"""
        self.output("[DEBUG] " + text, verbose)

    def info(self, text, verbose=2):
        """Information level output"""
        self.output("[INFO] " + text, verbose)

    def warn(self, text, verbose=1):
        """Warning level output"""
        self.output("[WARNING] " + text, verbose)

    def err(self, text, verbose=0):
        """Error level output"""
        self.output("[ERROR] " + text, verbose)


class GceManager(object):
    """Google Compute Engine Manager"""

    def __init__(self):
        """__init__"""
        self.params = {
            "service_account_file": "",
            "project": "",
            "zone": "",
            "instance": "",
            "scopes": ["https://www.googleapis.com/auth/compute"],
            "config_file": os.environ["HOME"] + "/.config/gce-manager/config",
            "verbose": 2,
        }
        self.output = Output(self.params["verbose"])

    def debug(self, text, verbose=3):
        """Debug level output wrapper"""
        self.output.debug(text, verbose)

    def info(self, text, verbose=2):
        """Information level output wrapper"""
        self.output.info(text, verbose)

    def warn(self, text, verbose=1):
        """Warning level output wrapper"""
        self.output.warn(text, verbose)

    def err(self, text, verbose=0):
        """Error level output wrapper"""
        self.output.err(text, verbose)

    def set_params(self, params):
        """Set parameters"""
        for (k, v) in params.items():
            self.params[k] = v
        self.output.set_verbose(self.params["verbose"])

    def read_config(self):
        """Read configuration file"""
        if os.path.isfile(self.params["config_file"]):
            params = {}
            with open(self.params["config_file"]) as conf_file:
                for line in conf_file:
                    line_orig = line
                    if line.find("#") != -1:
                        line = line.split("#")[0].strip()
                    if line == "":
                        continue
                    if line.find("=") == -1 or len(line.split("=")) > 2:
                        self.warn("Wrong configuration line: " + line_orig)
                        continue
                    (k, v) = line.split("=")
                    params[k.strip()] = v.strip()
            self.set_params(params)

    def build_compute(self):
        """Auth and Build"""
        credentials = service_account.Credentials.from_service_account_file(
            self.params["service_account_file"].replace("~",
                                                        os.environ["HOME"]),
            scopes=self.params["scopes"])
        return build("compute", "v1", credentials=credentials)

    def get_zones(self, compute, project):
        """Make zone list"""
        return compute.zones().list(project=project).execute()

    def print_zones(self, compute, project):
        """Print zone information"""
        import json
        zones = self.get_zones(compute, project)
        if "items" not in zones:
            return
        if self.params["verbose"] > 2:
            print(json.dumps(zones["items"], indent=4, separators=(",", ": ")))
        else:
            for zone in zones["items"]:
                print(zone["name"])

    def get_zones_instances(self, compute, project):
        """Make instance list for all zones"""
        zones_instances = {}
        zones = self.get_zones(compute, project)
        if "items" not in zones:
            return zones_instances
        for zone in [x["name"] for x in zones["items"]]:
            instances = self.get_instances(compute, project, zone)
            if "items" not in instances:
                continue
            for instance in instances["items"]:
                if not zone in zones_instances:
                    zones_instances[zone] = []
                zones_instances[zone].append(
                    instance["name"] + ": " + instance["status"])
        return zones_instances

    def print_zones_instances(self, compute, project):
        """Print instances for all zones"""
        zones_instances = self.get_zones_instances(compute, project)
        for k, v in zones_instances.items():
            print(k + ":")
            for i in v:
                print("  " + i)

    def get_instances(self, compute, project, zone):
        """Make instance list"""
        return compute.instances().list(project=project, zone=zone).execute()

    def print_instances(self, compute, project, zone):
        """Print instances information"""
        import json
        instances = self.get_instances(compute, project, zone)
        if "items" not in instances:
            return
        if self.params["verbose"] > 2:
            print(json.dumps(instances["items"], indent=4,
                             separators=(",", ": ")))
        else:
            for instance in instances["items"]:
                print(instance["name"] + ": " + instance["status"])

    def get_instance(self, compute, project, zone, instance):
        """Get each instance information"""
        result = compute.instances().get(project=project, zone=zone,
                                         instance=instance).execute()
        return result

    def print_instance(self, compute, project, zone, instance):
        """Print each instance information"""
        import json
        myinstance = self.get_instance(compute, project, zone, instance)
        if self.params["verbose"] > 2:
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

    def start(self, compute, project, zone, instance):
        """Start instance"""
        import json
        result = compute.instances().start(project=project, zone=zone,
                                           instance=instance).execute()
        print(json.dumps(result, indent=4, separators=(",", ": ")))

    def stop(self, compute, project, zone, instance):
        """Stop instance"""
        import json
        result = compute.instances().stop(project=project, zone=zone,
                                          instance=instance).execute()
        print(json.dumps(result, indent=4, separators=(",", ": ")))

    def execute(self, argv=None):
        """Main function"""

        self.read_config()

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
        help_doc = "List up instances for all zones"
        subparsers.add_parser("zones_instances", description=help_doc,
                              help=help_doc,
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
                            action="store",
                            default=self.params["service_account_file"],
                            help="Set service account file")
        parser.add_argument("-p", "--project",
                            action="store", default=self.params["project"],
                            help="Set project ID")
        parser.add_argument("-z", "--zone",
                            action="store", default=self.params["zone"],
                            help="Set zone")
        parser.add_argument("-i", "--instance",
                            action="store", default=self.params["instance"],
                            help="Set service account file")
        parser.add_argument("-v", "--verbose", type=int,
                            action="store", default=self.params["verbose"],
                            help="Verbose level"
                            " (0:error, 1: warning, 2: info, 3: debug)")
        parser.add_argument("-h", "--help",
                            action="store_true",
                            help="Print Help (this message)")

        if argv is None:
            argv = sys.argv[1:]
        command = None
        for a in argv:
            if a in subparsers.choices:
                if command is not None:
                    self.err("More than two commands are given: " +
                             command + ", " + a)
                    return 20
                command = a
        if command is not None:
            argv.remove(command)
            argv.append(command)

        args = parser.parse_args(argv)

        if args.help or args.command == "help" or args.command is None:
            parser.print_help()
            return 0
        self.set_params(vars(args))

        need_service_account_file = ["instances", "zones", "zones_instances",
                                     "start", "stop", "get"]
        need_project = ["instances", "zones", "zones_instances",
                        "start", "stop", "get"]
        need_zone = ["instances", "start", "stop", "get"]
        need_instance = ["start", "stop", "get"]


        if self.params["command"] in need_service_account_file and\
                self.params["service_account_file"] == "":
            self.err("Please set account service file")
            return 10
        if self.params["command"] in need_project and\
                self.params["project"] == "":
            self.err("Please set project ID")
            return 11
        if self.params["command"] in need_zone and self.params["zone"] == "":
            self.err("Please set zone")
            return 12
        if self.params["command"] in need_instance and\
                self.params["instance"] == "":
            self.err("Please set instance")
            return 13

        compute = self.build_compute()

        if self.params["command"] == "instances":
            self.print_instances(compute, self.params["project"],
                                 self.params["zone"])
        elif self.params["command"] == "zones":
            self.print_zones(compute, self.params["project"])
        elif self.params["command"] == "zones_instances":
            self.print_zones_instances(compute, self.params["project"])
        elif self.params["command"] == "start":
            self.start(compute, self.params["project"], self.params["zone"],
                       self.params["instance"])
        elif self.params["command"] == "stop":
            self.stop(compute, self.params["project"], self.params["zone"],
                      self.params["instance"])
        elif self.params["command"] == "get":
            self.print_instance(compute, self.params["project"],
                                self.params["zone"], self.params["instance"])
        return 0

if __name__ == "__main__":
    gm = GceManager()
    ret = gm.execute()
    sys.exit(ret)
