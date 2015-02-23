import cfg
import queue
import re
import socket
import time

MSG_PREFIX = r"^:\w+!\w+@\w+\.tmi\.twitch\.tv "
CHAT_MSG = re.compile(MSG_PREFIX + r"PRIVMSG #\w+ :")

def msg_send(sock, message):
    sock.send((message + "\r\n").encode("utf-8"))

def main():
    s = socket.socket()
    s.connect((cfg.HOST, cfg.PORT))

    send_queue = queue.PriorityQueue()
    msg_send(s, "PASS " + cfg.PASS)
    msg_send(s, "NICK " + cfg.NICK)
    msg_send(s, "JOIN " + cfg.CHAN)

    while True:
        lines = s.recv(4096).decode("utf-8").split("\r\n")

        for line in lines:
            if line == "PING :tmi.twitch.tv":
                send_queue.put((0, "PONG :tmi.twitch.tv"))
                print(line)
            elif CHAT_MSG.match(line):
                print(CHAT_MSG.sub(re.search(r"\w+", line).group(0) + ": ", line), end="")
            else:
                pass

        try:
            s.send((send_queue.get(timeout=0)[1] + "\r\n").encode("utf-8"))
        except queue.Empty:
            pass
        time.sleep(1 / cfg.RATE)

if __name__ == "__main__":
    main()
