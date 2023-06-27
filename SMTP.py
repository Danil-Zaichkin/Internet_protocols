import random
import ssl
import socket

import base64
import json
import os

import argparse

from pathlib import Path


def read_txt_file(file_name: str):
    with open(file_name, "r", encoding="UTF-8") as file_txt:
        return file_txt.read()


def read_json_file(file_name: str):
    with open(file_name, "r", encoding="UTF-8") as file_json:
        return json.load(file_json)


def get_send_type_file(type_file):
    if type_file == "txt":
        return "text/plain"
    elif type_file == "html":
        return "text/html"
    elif type_file == "jpg" or type_file == "jpeg" or type_file == "png" \
            or type_file == "gif":
        return f"image/{type_file}"
    elif type_file == "mpeg" or type_file == "wav":
        return f"audio/{type_file}"
    elif type_file == "mp4" or type_file == "mpeg":
        return f"video/{type_file}"
    elif type_file == "pdf" or type_file == "zip":
        return f"application/{type_file}"
    elif type_file == "doc":
        return "application/msword"
    elif type_file == "docx":
        return "application/vnd.openxmlformats-officedocument" \
               ".wordprocessingml.document "
    elif type_file == "xls":
        return "application/vnd.ms-excel"
    elif type_file == "xlsx":
        return "application/vnd.openxmlformats-officedocument.spreadsheetml" \
               ".sheet "
    elif type_file == "ppt":
        return "application/vnd.ms-powerpoint"
    elif type_file == "pptx":
        return "application/vnd.openxmlformats-officedocument.presentationml" \
               ".presentation "
    else:
        return False


def prepare_files(directory_path: str):
    dict_files_info = {}

    for file_name in os.listdir(directory_path):
        path_file = os.path.join(directory_path, file_name)
        if os.path.isfile(path_file):
            with open(path_file, "rb") as byte_file:
                base64file = base64.b64encode(byte_file.read()).decode(
                    "UTF-8")
            type_file = get_send_type_file(
                os.path.splitext(file_name)[1][1:])
            if type_file:
                dict_files_info[file_name] = [base64file, type_file]
            else:
                print(f"{file_name}: failed to recognized the type")

    return dict_files_info


def send_request(client_socket: ssl.SSLSocket, data_request: str):
    client_socket.send((data_request + '\n').encode())
    receive_response(client_socket)


def receive_response(client_socket: ssl.SSLSocket):
    client_socket.settimeout(1)
    while True:
        try:
            recv_data = client_socket.recv(1024).decode("UTF-8")
            print(recv_data)
        except socket.timeout:
            break


def generate_boundary():
    list_number = [n for n in range(0, 10)]
    random_number = ""
    for _ in range(6):
        random_number += str(random.choice(list_number))
    return f"bound.{random_number}"


class SMTPClient:
    def __init__(self, config_dict: dict, file_psw: str, file_msg: str):

        self.smtp_host = "smtp.yandex.ru"
        self.smtp_port = 465

        self.user_password = read_txt_file(file_psw)

        self.user_name_from = config_dict["from"]
        self.user_name_to_list = config_dict["to"]
        self.subject_message = config_dict["subject"]
        self.text_message = read_txt_file(file_msg)
        self.send_files_dict = prepare_files(
            config_dict["path_directory_files"])

    def message_prepare(self, user_name_to: str):
        boundary_msg = generate_boundary()

        # заголовки
        headers = f'from: {self.user_name_from}\n'
        headers += f'to: {user_name_to}\n'
        headers += f'subject: {self.subject_message}\n'
        headers += 'MIME-Version: 1.0\n'
        headers += 'Content-Type: multipart/mixed;\n' \
                   f'    boundary={boundary_msg}\n'

        # тело сообщения началось
        message_body = f'--{boundary_msg}\n'
        message_body += 'Content-Type: text/plain; charset=utf-8\n\n'
        message_body += self.text_message + '\n'
        message_body += f'--{boundary_msg}\n'
        for send_file in self.send_files_dict:
            message_body += f'Content-Disposition: attachment;\n' \
                            f'   filename={send_file}\n'
            message_body += 'Content-Transfer-Encoding: base64\n'
            message_body += f'Content-Type: ' \
                            f'{self.send_files_dict[send_file][1]};\n\n '
            message_body += self.send_files_dict[send_file][0] + '\n'
            message_body += f'--{boundary_msg}\n'

        message_body += f'--{boundary_msg}--'
        message = headers + '\n' + message_body + '\n.\n'
        return message

    def send_message(self):
        base64login = base64.b64encode(self.user_name_from.encode()).decode()
        base64password = base64.b64encode(self.user_password.encode()).decode()
        ssl_contex = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_contex.check_hostname = False
        ssl_contex.verify_mode = ssl.CERT_NONE

        try:
            with socket.create_connection(
                    (self.smtp_host, self.smtp_port)) as sock:
                try:
                    with ssl_contex.wrap_socket(sock,
                                                server_hostname=self.smtp_host) as client:
                        receive_response(client)  # в smpt сервер первый говорит

                        send_request(client, f'ehlo {socket.gethostname()}')
                        send_request(client, 'AUTH LOGIN')
                        send_request(client, base64login)
                        send_request(client, base64password)

                        for user_name_to in self.user_name_to_list:
                            send_request(client,
                                         f'MAIL FROM:{self.user_name_from}')
                            send_request(client, f"RCPT TO:{user_name_to}")
                            send_request(client, 'DATA')
                            send_request(client,
                                         self.message_prepare(user_name_to))
                except ssl.SSLError as e:
                    print(f"Ошибка SSL: {e}")
        except socket.error as e:
            print(f"Ошибка сокета: {e}")


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--config", type=Path,
                        help="path to config file", required=True)
    parser.add_argument("--password", type=Path,
                        help="path to password file", required=True)
    parser.add_argument("--msg", type=Path, help="path to content file",
                        required=True)
    args = parser.parse_args()

    config_file = args.config
    password_file = args.password
    msg_file = args.msg

    client_smtp = SMTPClient(
        read_json_file(config_file),
        password_file,
        msg_file
    )
    client_smtp.send_message()


if __name__ == "__main__":
    main()
