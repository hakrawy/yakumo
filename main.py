#!/usr/bin/env python
##########################################################################
##########################################################################
####                                                                  ####
####                               YAKUMO                             ####
####                 AUTOMATIC PROXY GRABBER + CHECKER                ####
####                                                                  ####
####                         by elliottophellia                       ####
####                                                                  ####
##########################################################################
####             https://github.com/elliottophellia/yakumo            ####
##########################################################################
####                Buy Me A Coffie : https://rei.my.id               ####
##########################################################################
####                             Credits to:                          ####
####               mmpx12, monosans, TheSpeedX, hookzof               ####
##########################################################################


import os
import re
import json
import asyncio
import aiohttp
import aiohttp_socks
from pathlib import Path

RED = "\033[31m"
CLEAR = "\033[0m"
GREEN = "\033[32m"
YELLOW = "\033[33m"

async def check_proxy(type, proxy):
    try:
        timeout = aiohttp.ClientTimeout(total=30)
        connector = aiohttp_socks.ProxyConnector.from_url(f"{type}://{proxy}")
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            try:
                async with session.get("https://httpbin.org/ip") as response:
                    try:
                        result = await response.json()
                        ip = re.findall(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', proxy)
                        if result['origin'] == ip[0]:
                            print(f'{GREEN}[+]{CLEAR} {proxy} is {GREEN}live{CLEAR}')
                            with open(f'results/{type}/{type}_checked.txt', 'a') as f:
                                f.write(proxy + '\n')
                        else:
                            print(f'{RED}[-]{CLEAR} {proxy} is {RED}dead{CLEAR}')
                    except json.JSONDecodeError:
                        print(f'{YELLOW}[!]{CLEAR} {proxy} is {YELLOW}returned non-JSON response{CLEAR}')
            except ConnectionResetError:
                print(f'{RED}[-]{CLEAR} {proxy} is {RED}dead{CLEAR}')
            except:
                print(f'{RED}[-]{CLEAR} {proxy} is {RED}dead{CLEAR}')
            finally:
                rmold = Path(f'results/{type}/{type}.txt')
                if rmold.exists():
                    rmold.unlink()
    except:
        print(f'{RED}[-]{CLEAR} Invalid proxy format: {proxy}')

async def checker(type):
    with open(f"results/{type}/{type}.txt", "r") as f:
        data = f.read().split("\n")
    data = [proxy for proxy in data if proxy]
    print(f'{YELLOW}[>]{CLEAR} {GREEN}{len(data)}{CLEAR} {type} proxies will be checked')

    checked_file = Path(f'results/{type}/{type}_checked.txt')
    if checked_file.exists():
        checked_file.unlink()

    tasks = [check_proxy(type, i) for i in data]
    await asyncio.gather(*tasks)

async def fetch(url):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.text()
        except:
            print(f"An error occurred while fetching {url}.")
            return None

async def fetch_all(urls):
    tasks = [fetch(url) for url in urls]
    results = await asyncio.gather(*tasks)
    return results

sources = {
    "http": [
        "https://raw.githubusercontent.com/mmpx12/proxy-list/master/https.txt",
        "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt"
    ],
    "socks4": [
        "https://raw.githubusercontent.com/mmpx12/proxy-list/master/socks4.txt",
        "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks4.txt",
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt"
    ],
    "socks5": [
        "https://raw.githubusercontent.com/mmpx12/proxy-list/master/socks5.txt",
        "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt",
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt",
        "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt"
    ]
}

def handle_exception(loop, context):
    exception = context.get('exception')
    if isinstance(exception, ConnectionResetError):
        print(f'{RED}[-]{CLEAR} Connection was reset by the remote host')
    else:
        loop.default_exception_handler(context)

async def main():
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(handle_exception)

    if not os.path.exists('results'):
        os.makedirs('results')

    for type, urls in sources.items():
        if not os.path.exists(f'results/{type}'):
            os.makedirs(f'results/{type}')

        file = Path(f'results/{type}/{type}.txt')
        if file.exists():
            file.unlink()

        results = await fetch_all(urls)
        proxies = set()

        for result in results:
            if result:
                proxies.update(result.splitlines())
                with open(f'results/{type}/{type}.txt', 'a') as f:
                    for proxy in proxies:
                        f.write(proxy + '\n')
        await checker(type)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass