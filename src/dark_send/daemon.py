from dark_send.core import daemonize
import asyncio

def main():
    asyncio.run(daemonize())

if __name__ == "__main__":
    main()

