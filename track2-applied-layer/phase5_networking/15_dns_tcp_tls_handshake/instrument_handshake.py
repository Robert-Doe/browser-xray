"""
Module 15: dns_tcp_tls_handshake -- what "loading a URL" actually costs
before a single byte of the page itself arrives.

Instruments, with real timing and real captured data, the three
layered steps that happen before ANY HTML reaches a browser:
  1. DNS resolution      -- turn a hostname into an IP address
  2. TCP handshake        -- establish a reliable byte-stream connection
  3. TLS handshake        -- negotiate an encrypted, authenticated channel

Every number and every certificate field printed here comes from a
REAL connection to a real server -- no simulated timings, no invented
certificate data.
"""

import socket
import ssl
import time

HOSTNAME = "example.com"
PORT = 443


def step_dns_resolution(hostname: str) -> str:
    print(f"--- Step 1: DNS resolution for {hostname!r} ---")
    start = time.perf_counter()
    results = socket.getaddrinfo(hostname, PORT, proto=socket.IPPROTO_TCP)
    elapsed = time.perf_counter() - start

    addresses = sorted({r[4][0] for r in results})
    print(f"  resolved {len(addresses)} address(es) in {elapsed * 1000:.2f} ms:")
    for addr in addresses:
        print(f"    {addr}")
    chosen = addresses[0]
    print(f"  using: {chosen}\n")
    return chosen


def step_tcp_handshake(ip: str, hostname: str) -> socket.socket:
    print(f"--- Step 2: TCP handshake to {ip}:{PORT} ---")
    start = time.perf_counter()
    sock = socket.create_connection((ip, PORT), timeout=10)
    elapsed = time.perf_counter() - start

    local_addr, local_port = sock.getsockname()
    print(f"  connected in {elapsed * 1000:.2f} ms")
    print(f"  local endpoint:  {local_addr}:{local_port} (an ephemeral port, "
          f"chosen by the OS for this one connection)")
    print(f"  remote endpoint: {ip}:{PORT}\n")
    return sock


def step_tls_handshake(sock: socket.socket, hostname: str) -> ssl.SSLSocket:
    print(f"--- Step 3: TLS handshake (server_hostname={hostname!r}) ---")
    context = ssl.create_default_context()

    start = time.perf_counter()
    tls_sock = context.wrap_socket(sock, server_hostname=hostname)
    elapsed = time.perf_counter() - start

    cert = tls_sock.getpeercert()
    subject = dict(x[0] for x in cert["subject"])
    issuer = dict(x[0] for x in cert["issuer"])

    print(f"  handshake completed in {elapsed * 1000:.2f} ms")
    print(f"  negotiated protocol: {tls_sock.version()}")
    print(f"  negotiated cipher:   {tls_sock.cipher()[0]}")
    print(f"  certificate subject: {subject.get('commonName')}")
    print(f"  certificate issuer:  {issuer.get('organizationName')} / {issuer.get('commonName')}")
    print(f"  certificate valid until: {cert['notAfter']}\n")
    return tls_sock


def step_send_request(tls_sock: ssl.SSLSocket, hostname: str) -> None:
    print(f"--- Step 4: send a real HTTP request over the encrypted channel ---")
    request = (
        f"HEAD / HTTP/1.1\r\n"
        f"Host: {hostname}\r\n"
        f"Connection: close\r\n"
        f"User-Agent: browser-xray-course-module15\r\n"
        f"\r\n"
    ).encode("ascii")

    start = time.perf_counter()
    tls_sock.sendall(request)
    response = tls_sock.recv(4096)
    elapsed = time.perf_counter() - start

    print(f"  round trip in {elapsed * 1000:.2f} ms")
    first_line = response.split(b"\r\n", 1)[0].decode("ascii", errors="replace")
    print(f"  first response line: {first_line!r}")
    print(
        "  (this is headers only -- HEAD deliberately requests no body -- "
        "not one byte of an actual HTML PAGE has been parsed by anything yet)\n"
    )

    print("  --- X-ray: the first 64 raw bytes actually received, in hex ---")
    chunk = response[:64]
    hex_bytes = " ".join(f"{b:02X}" for b in chunk)
    ascii_repr = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
    print(f"  {hex_bytes}")
    print(f"  {ascii_repr}")
    print(
        "  (this readable ASCII is only visible here because TLS already "
        "decrypted it for us -- anyone watching the actual network link sees "
        "only opaque ciphertext for every one of these bytes)"
    )


def main() -> None:
    ip = step_dns_resolution(HOSTNAME)
    tcp_sock = step_tcp_handshake(ip, HOSTNAME)
    tls_sock = step_tls_handshake(tcp_sock, HOSTNAME)
    step_send_request(tls_sock, HOSTNAME)
    tls_sock.close()


if __name__ == "__main__":
    main()
