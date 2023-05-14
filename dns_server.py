import socket
import dnslib
import pickle
import time
from pathlib import Path
from collections import defaultdict

AUTHORITATIVE_SERVER = '213.180.193.1'  # ns1.yandex.ru


class DNSServer:
    def __init__(self, port, cache_path: Path):
        self.cache_path = cache_path
        self.cache = self._init_cache()
        self.port = port

    def _init_cache(self):
        try:
            with open(self.cache_path, 'rb') as file:
                data = pickle.load(file)
                res_cache = {}
                for key, (response, ttl) in data.items():
                    if time.time() < ttl:
                        res_cache[key] = (response, ttl)
                return res_cache
        except FileNotFoundError:
            return {}

    def save_cache(self):
        with open(self.cache_path, 'wb') as file:
            pickle.dump(self.cache, file)

    def get_response(self, key):
        response = self.cache.get(key)
        if response is None:
            return
        response_data, ttl = response
        if time.time() > ttl:
            del self.cache[key]
            return
        return response_data

    def save_response(self, key, response, ttl):
        res_ttl = time.time() + ttl
        self.cache[key] = (response, res_ttl)

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.bind(('', self.port))
            while True:
                try:
                    data, address = s.recvfrom(1024)
                    response = self.handle_query(data)
                    s.sendto(response, address)
                except Exception as e:
                    print(e)

    def handle_query(self, data):
        query = dnslib.DNSRecord.parse(data)
        key = query.q.qname, query.q.qtype
        cache_response = self.get_response(key)
        if cache_response:
            response = dnslib.DNSRecord(header=query.header)
            response.add_question(query.q)
            response.rr.extend(cache_response)
            print(f'{key} from cache')
            return response.pack()
        response = query.send(AUTHORITATIVE_SERVER, 53, timeout=4)
        response = dnslib.DNSRecord.parse(response)
        if response.header.rcode == dnslib.RCODE.NOERROR:
            records = (response.rr, response.auth, response.ar)
            records_dict = defaultdict(list)
            for record in records:
                for rr in record:
                    records_dict[rr.rname, rr.rtype].append(rr)
                    self.save_response((rr.rname, rr.rtype),
                                       records_dict[rr.rname, rr.rtype],
                                       rr.ttl
                                       )
        return response.pack()


if __name__ == '__main__':
    server = DNSServer(53, Path('cache'))
    try:
        server.start()
    except KeyboardInterrupt:
        server.save_cache()
