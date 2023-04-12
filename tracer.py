import os
import re
import json
from urllib.request import urlopen
from argparse import ArgumentParser
from collections import defaultdict

from tabulate import tabulate


class Tracer:
    def __init__(self, name: str):
        self._IP_REGEX = re.compile(
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"
        )
        self._name = name

    def _get_trace_route(self) -> list[str]:
        os.system(f'tracert {self._name} > route.txt')
        with open('route.txt', 'r') as file:
            ips = re.findall(self._IP_REGEX, file.read())
            return ips[1:]

    @staticmethod
    def get_ip_info(ip: str):
        ip_info = json.loads(urlopen(f"https://ipinfo.io/{ip}/json").read())
        ip_info_dict = defaultdict(str)
        ip_info_dict['ip'] = ip

        if 'org' in ip_info.keys():
            ip_org_info = ip_info['org'].split()
            asn = ip_org_info[0]
            provider = ' '.join(ip_org_info[1:])
            ip_info_dict['asn'] = asn
            ip_info_dict['country'] = ip_info['country']
            ip_info_dict['provider'] = provider

        return ip_info_dict

    def get_trace_route_info(self):
        route = self._get_trace_route()
        route_info = []
        for num, ip in enumerate(route):
            ip_info = self.get_ip_info(ip)
            ip_info['№'] = str(num)
            route_info.append(ip_info)
        return tabulate(route_info, headers='keys')


def parse_args():
    parser = ArgumentParser(description='Tracing autonomous systems')
    parser.add_argument('name', type=str, help='ip address or '
                                               'domain name of target')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    tr = Tracer(args.name)
    print(tr.get_trace_route_info())
