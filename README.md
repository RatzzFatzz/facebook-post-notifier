[ci]: https://ci.pcgamingfreaks.at/job/zeitgeist-notifier/
[ciImg]: https://ci.pcgamingfreaks.at/job/zeitgeist-notifier/badge/icon
[dockerhub]: https://hub.docker.com/r/ratzzfatzz/zeitgeist-notifier
[license]: https://github.com/RatzzFatzz/zeitgeist-notifier/blob/master/LICENSE
[licenseImg]: https://img.shields.io/github/license/RatzzFatzz/zeitgeist-notifier.svg


[![ciImg]][ci] [![licenseImg]][license]

# Features:
- Automated notification if desired ice cream flavors are available today
- Select for which shop you want to get notified

# Requirements
- Telegram
- Telegram Bot
- Docker

# Docker setup
## Config
- Create config based on `config-template`
- Create a file named `data` and `cookie`
- Paste the cookies of `facebook.com` from your browser into `cookie`
- Example:
```
zeitgeist_notifier_config/
├── config
├── cookie
└── data

```
## Run docker
```
docker run --name zeitgeist-notifier <path-to-config-dir>:/config ratzzfatzz/zeitgeist-notifier:latest
```
## Docker-compose
```
version: "3.6"
services:
    zeitgeist-notifier:
        image: ratzzfatzz/zeitgeist-notifier:latest
        container_name: zeitgeist-notifier
        restart: unless-stopped
        volumes:
            - <path-to-config-dir>:/config
```

# Links
- [Docker Image][dockerhub]