# tg-theatres-monitor
parse and notify about upcoming events in my area

parser is generic and simple. modify your configurations [here](monitor/parser/theatres_cfg.yaml)

check out the awesome [Taskfile](Taskfile.yml) to explore commands!

how to use:
create and configure your .env with variables:
```
BOT_ID=<your bot id>
CHAT_ID=<your chat id>
```

build your bot with

```
docker build -f Dockerfile -t theatres .
```

run your bot once with:
```
docker run --env-file .env theatres
```

or configure a cronjob as:
```
* * * * * docker run --rm --env-file /absolute/path/to/.env theatres >> /path/to/logdir/tg_theatre.log
```

enjoy! 🤗
