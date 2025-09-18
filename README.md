# SSH-Cracker
The SSH Cracker project requires students to develop a Python script that brute-forces SSH credentials by testing username-password combinations against a target host. Two solutions are provided: ssh_brute.py (basic, sequential brute-forcing) and advance_ssh_brute.py (advanced, with multithreading, password generation, and retry logic). Both use the paramiko library for SSH connections, socket for network handling, colorama for colored output, and argparse for command-line arguments, with the advanced version adding itertools, threading, queue, and contextlib.

# Features:
Multithreaded login attempts for speed.
Option to use a password list or generate passwords on the fly.
Configurable retry and delay mechanism for handling SSH exceptions.

# Prerequisites:
Python 3.x
paramiko
colorama
Install dependencies: pip install paramiko colorama

# Usage: 
python ssh_audit.py <host> -u <username> -w <wordlist.txt> [options]

# Key options:
Option	Description
-u / --user	Single username to test
-U / --userlist	File containing list of usernames
-w / --wordlist	File containing list of passwords
-g / --generate	Generate passwords instead of using a wordlist
--min_length / --max_length	Length range for generated passwords
-c / --chars	Characters for password generation
-t / --threads	Number of concurrent threads (default: 4)
--port	SSH port (default: 22)
