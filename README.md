# albatross
Albatross is a modular mid-level network stress testing and simulating DDoS (Distributed Denial-of-Service) scenarios

This Python tool runs multiple concurrent bots that repeatedly perform:

- An SSL handshake check using OpenSSL (`openssl s_client`)  
- An HTTPS GET request with randomized User-Agent headers  

It logs the results (timestamps, SSL success, cert issuer & expiry, HTTP status & response time, user-agent) to a CSV file.

---

## Requirements

- Python 3.7+  
- OpenSSL CLI installed (`openssl` command available)  
- Python package: `requests`

Install the package with:

```bash
pip install -r requirements.txt
```

---

## Usage

```bash
python albatross.py TARGET_HOST [options]
```

### Options

| Option           | Description                                   | Default       |
|------------------|-----------------------------------------------|---------------|
| `-p, --port`     | Target port (usually 443)                     | 443           |
| `-d, --duration` | Duration of the test in minutes               | 3             |
| `-b, --bots`     | Number of concurrent bots (threads)           | 3             |
| `--min-interval` | Minimum seconds between checks per bot        | 3             |
| `--max-interval` | Maximum seconds between checks per bot        | 7             |
| `-o, --output`   | CSV output filename                           | results.csv   |

---

## Example

Run 5 bots for 5 minutes with 2-6 seconds randomized interval:

```bash
python albatross.py example.com -b 5 -d 5 --min-interval 2 --max-interval 6 -o results.csv
```

---

## Graceful Shutdown

Press Ctrl+C to stop the test early; results collected so far will be saved.

---

## Notes

- Requires `openssl` CLI tool installed and in your PATH.  
- Random User-Agent headers simulate diverse clients.  
- This tool is intended for authorized testing only. Do not use against unauthorized targets.
- Need 1000 Mbps internet bandwith with stable connection 
