import json
import logging
import aiohttp
import asyncio
import tqdm


async def browsing_get(sem, url: str, headers: dict, session: aiohttp.ClientSession) -> bytes:
    """ Get info """
    async with sem:
        async with session.get(url, headers=headers, ssl=False) as request:
            if request.status == 200:
                return await request.read()
            else:
                return b'[]'


async def browsing_join(url_base: list, headers: dict, max_sessions: int) -> list:
    """ Control asinc getting pages """
    tasks = []
    sem = asyncio.Semaphore(max_sessions)
    async with aiohttp.ClientSession() as session: 
        for url in url_base:
            task = asyncio.ensure_future(browsing_get(sem, url, headers, session))
            tasks.append(task)
        for future in tqdm.tqdm(tasks, total=len(url_base)):
            await future
    return await asyncio.gather(*tasks)


async def browsing_get_header(sem, record: dict, headers: dict, session: aiohttp.ClientSession) -> dict:
    """ Get X-Total from header and add to dict """
    async with sem:
        async with session.get(record['url'], headers=headers, ssl=False) as request:
            if request.status == 200:
                record['total'] = int(request.headers['X-Total'])
                return record
            else:
                return record


async def browsing_header(base: list, headers: dict, max_sessions: int) -> list:
    """ Control asinc getting pages """
    tasks = []
    sem = asyncio.Semaphore(max_sessions)
    async with aiohttp.ClientSession() as session: 
        for each in base:
            task = asyncio.ensure_future(browsing_get_header(sem, each, headers, session))
            tasks.append(task)
        for future in tqdm.tqdm(tasks, total=len(base)):
            await future
    return await asyncio.gather(*tasks)


async def browsing_get_tags(sem, url: str, headers: dict, session: aiohttp.ClientSession) -> dict:
    """ Get info """
    async with sem:
        async with session.get(url, headers=headers, ssl=False) as request:
            if request.status == 200:
                data = await request.read()
                return {'url': url, 'data': json.loads(data)}
            else: 
                logging.error(f'Cant get tags from {url}')


async def browsing_join_tags(url_base: list, headers: dict, max_sessions: int) -> list:
    """ Control asinc getting pages """
    tasks = []
    sem = asyncio.Semaphore(max_sessions)
    async with aiohttp.ClientSession() as session: 
        for url in url_base:
            task = asyncio.ensure_future(browsing_get_tags(sem, url, headers, session))
            tasks.append(task)
        for future in tqdm.tqdm(tasks, total=len(url_base)):
            await future
    return await asyncio.gather(*tasks)


async def browsing_del_tags(sem, url: str, headers: dict, session: aiohttp.ClientSession) -> str:
    """ Deleting tags """
    async with sem:
        async with session.delete(url, headers=headers, ssl=False) as request:
            if request.status == 200:
                return url
            else: 
                logging.error(f'Cant delete tag {url}')
                return f'--=Cant delete=--{url}'


async def browsing_join_del_tags(url_base: list, headers: dict, max_sessions: int) -> list:
    """ Control asinc deleting """
    tasks = []
    sem = asyncio.Semaphore(max_sessions)
    async with aiohttp.ClientSession() as session: 
        for url in url_base:
            task = asyncio.ensure_future(browsing_del_tags(sem, url, headers, session))
            tasks.append(task)
        for future in tqdm.tqdm(tasks, total=len(url_base)):
            await future
    return await asyncio.gather(*tasks)


def get_registry(api_v4_url: str, headers: dict, project_id: int, max_connections: int) -> list:
    registry = list()
    registry_urls = list()
    repos = list()
    repo_urls = [f"{api_v4_url}/projects/{project_id}/registry/repositories"]
    response = asyncio.run(browsing_join(repo_urls, headers, max_connections))
    for each in response:
        tmp = json.loads(each)
        if tmp:
            repos += tmp
    for repo in repos:
        repo['url'] = f"{api_v4_url}/projects/{repo['project_id']}/registry/repositories/{repo['id']}/tags"
    repos = asyncio.run(browsing_header(repos, headers, max_connections))
    for repo in repos:
        if repo['total'] % 100 > 0:
            total_pages = repo['total'] // 100 + 1
        else:
            total_pages = repo['total'] // 100
        registry_urls += [repo['url'] + '?per_page=100&page=' + str(page) for page in range(1, total_pages + 1)]
    response = asyncio.run(browsing_join_tags(registry_urls, headers, max_connections))
    for each in response:
        for tag in each['data']:
            tag['del_url'] = each['url'][:each['url'].find('?')] + '/' + tag['name']
        each['data'] = [tag for tag in each['data'] if tag['name'] != 'latest']
        registry += each['data']
    return registry


def del_registry_tags(url_base: list, headers: dict, max_sessions: int) -> list:
    return asyncio.run(browsing_join_del_tags(url_base, headers, max_sessions))
