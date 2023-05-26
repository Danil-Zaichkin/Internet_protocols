import socket
import ssl
import json
from argparse import ArgumentParser

HOST_ADDRESS = 'api.vk.com'
HTTPS_PORT = 443


def parse_args():
    parser = ArgumentParser(description='VK parser')
    parser.add_argument('user_id', type=str, help='user id for parsing')

    return parser.parse_args()


def get_user_fiends(token, user_id):
    ssl_contex = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ssl_contex.check_hostname = False
    ssl_contex.verify_mode = ssl.CERT_NONE

    with socket.create_connection((HOST_ADDRESS, HTTPS_PORT)) as sock:
        with ssl_contex.wrap_socket(sock,
                                    server_hostname=HOST_ADDRESS
                                    ) as client_socket:
            message = get_prepared_message(
                {
                    'method': 'GET',
                    'url': '/method/friends.get',
                    'params': {
                        'access_token': token,
                        'user_id': user_id,
                        'fields': 'nickname',
                        'v': '5.131',
                    },
                    'version': '1.1',
                    'headers': {'host': HOST_ADDRESS},
                    'body': None
                }
            )
            body = send_request(client_socket, message).split('\r\n\r\n')[-1]
            json_body = json.loads(body)
            return [f'{user["first_name"]} {user["last_name"]}' for user in
                    json_body['response']['items']]


def send_request(sock, request_message):
    sock.send(request_message.encode())
    sock.settimeout(1)
    recv_data = sock.recv(65535)
    while True:
        try:
            buf = sock.recv(65535)
            recv_data += buf
        except socket.timeout:
            break

    return recv_data.decode()


def get_prepared_message(data):
    message = data['method'] + ' ' + data['url'] + '?'
    params = '&'.join(
        [f'{arg}={value}' for arg, value in data['params'].items()])
    message += params
    message += ' ' + 'HTTP/' + data['version'] + '\n'
    for header, value in data['headers'].items():
        message += f'{header}: {value}\n'
    if data['body']:
        pass
    message += '\n'

    return message


def main():
    with open('token.txt', 'r') as f:
        token = f.readline()
    args = parse_args()
    for friend in get_user_fiends(token, args.user_id):
        print(friend)


if __name__ == '__main__':
    main()
