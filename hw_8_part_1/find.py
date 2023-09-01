import re
import sys
import redis
from redis_lru import RedisLRU

from models import Qoutes, Authors
import connect

client = redis.StrictRedis(host="localhost", port=6379, password=None)
cache = RedisLRU(client)


# docker run --name redis-cache -d -p 6379:6379 redis


@cache
def find_author(fullname):
    authors = Authors.objects(fullname=re.compile(f'.*{fullname}.*', re.IGNORECASE))
    return authors


@cache
def command_name(inp_str, *args):
    if len(inp_str) < 2:
        return f'Error: no name to find!'

    name = inp_str[1].strip()
    authors = find_author(name)

    if not authors:
        return f'There is no information about <{name}>'

    result = []
    authors_str = []
    for author in authors:
        for qoute in Qoutes.objects():
            if qoute.to_mongo().to_dict()['author'] == author['id']:
                authors_str.append(author['fullname'])
                result.append(qoute.to_mongo().to_dict()['qoute'])
    res = "\n".join(result)
    return f"The most famous qoutes by {', '.join(set(authors_str))}:\n{res}\n{'-' * 100}"


@cache
def command_tag(inp_str, *args):
    if len(inp_str) < 2:
        return f'Error: no tag to seek!'

    tag = inp_str[1].strip()
    tags = Qoutes.objects(tags=re.compile(f'.*{tag}.*', re.IGNORECASE))

    if not tags:
        return f'There is no information by tag <{tag}>'
    res = "\n".join([tag_['qoute'] for tag_ in tags])
    t = list(filter(lambda val: tag in val, [t for tag_ in tags for t in tag_['tags']]))
    tags_str = ", ".join(t)
    return f"Qoutes by tag <{tags_str}>:\n{res}\n{'-' * 100}"


@cache
def command_tags(inp_str, *args):
    if len(inp_str) < 2:
        return f'Error: no tag to seek!'

    tags = [tag.strip() for tag in inp_str[1].strip().split(',')]
    result = []
    for tag in tags:
        for qoute in Qoutes.objects():
            if tag in qoute.to_mongo().to_dict()['tags']:
                result.append(qoute.to_mongo().to_dict()['qoute'])

    if not result:
        return f'There is no information by tags <{tags}>'
    res = "\n".join(result)
    return f"Qoutes by tags <{tags}>:\n{res}\n{'-' * 100}"


def command_exit(*args):
    sys.exit('Good bye!')


command_dict = {
    'name': command_name,
    'tag': command_tag,
    'tags': command_tags,
    'exit': command_exit
}


def handler(command, *args):
    result = command_dict.get(command)
    if not result:
        return f"Command is not exist! Correct commands: tag, tags, name, exit"
    return result(*args)


def main():
    while True:
        inp_ = input('Write command: tag, tags, name, exit.\n-> ')
        arg_str = inp_.split(':')
        print(handler(arg_str[0].strip(), arg_str))


if __name__ == '__main__':
    main()
