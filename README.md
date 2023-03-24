# Hymns API

![CI](https://github.com/sopherapps/hymns-api/actions/workflows/CI.yml/badge.svg)

---

**Documentation:** [https://hymnsapi.sopherapps.com/docs](https://hymnsapi.sopherapps.com/docs)

--- 

This is a general API that can host hymns/songs including their musical notation.

## Notable Features:

 - Rate limited API
 - Publicly available READ-ONLY with need for an API Key
 - Privately accessible WRITE-ONLY with need of a JWT auth token for admins only
 - Very fast, due to use of embedded document-oriented database
 - Can have multiple translations for each song
 - CLI to do some devOps chores e.g. create new admin users etc.

## Contributing

Contributions are welcome. The docs have to maintained, the code has to be made cleaner, more idiomatic and faster,
and there might be need for someone else to take over this repo in case I move on to other things. It happens!

When you are ready, look at the [CONTRIBUTIONS GUIDELINES](./CONTRIBUTING.md)

## System Design

### Dependencies

- [Python v3.11+](https://python.org) - the programming language
- [FastAPI](https://fastapi.tiangolo.com/) - web server
- [Typer CLI](https://typer.tiangolo.com/typer-cli/) - for CLI commands
- [py_scdb](https://github.com/sopherapps/py_scdb) - embedded database
- [slowapi](https://pypi.org/project/slowapi/) - rate-limiting
- [pyotp](https://pyauth.github.io/pyotp/) - for one time passwords
- [fastapi-mail](https://sabuhish.github.io/fastapi-mail/) - for sending emails

### Major Design Decisions

- Each translation has its own scdb database, for scalability.
- The `user` records are in their own scdb database, for scalability.
- Access to different databases is done concurrently, for more speed.
- All business logic is put in appropriate services in the `services` folder
- All API related logic is in the `api` package, entry point being `main.py` in root folder.
- All CLI(command line interface) related logic is in the `cli` package, 
  entry point being `manage.py` in root folder.
- Any shared utility functions are found in the `utils` package or module in the package where
  they are needed e.g. services can have its own `utils`, api can also have its own `utils`,
  even the entire project can have its own `utils`.
- The `tests` package mirrors the folder structure followed by the project, 
  but with `test_` prefixes on the module names.


## Settings

| Environment Variable    | Meaning                                                                                | Default           |
|-------------------------|----------------------------------------------------------------------------------------|-------------------|
| DB_PATH                 | path to the scdb database folder                                                       | `./db`            |
| MAX_HYMNS               | maximum number of hymns to house in app                                                | 2000000           |
| DB_REDUNDANCY_BLOCKS    | number of redundant buffer blocks for extra keys in scdb                               | 2                 |
| DB_BUFFER_POOL_CAPACITY | scdb number of memory buffers                                                          | 5                 |
| DB_COMPACTION_INTERVAL  | scdb interval in seconds for compacting/defragmenting database files                   | 3600              |
| LANGUAGES               | comma-separated list of languages that the song bank will have                         | `english,runyoro` |
| API_KEY_LENGTH          | the length of the API keys generated                                                   | 32                |
| RATE_LIMIT              | the maximum number of requests per window (e.g. second) allowed from one IP address    | `5/minute`        |
| OTP_VERIFICATION_URL    | the url where the one-time password (OTP) are to be verified from                      |                   |
| API_SECRET              | the 32-byte API secret for hashing and encrypting stuff in the API                     |                   |
| JWT_TTL_SECONDS         | the JWT token's time-to-live in seconds                                                | 900               |
| ENABLE_RATE_LIMIT       | the flag for enabling/disabling rate-limiting                                          | `true`            |
| MAX_LOGIN_ATTEMPTS      | maximum number of attempts to feed in an OTP before being locked out.                  | 5                 |
| AUTH_MAIL_SENDER        | name of the person to put as email sender for all auth related emails                  | `Hymns API team`  |
| MAIL_USERNAME           | SMTP username                                                                          |                   |
| MAIL_PASSWORD           | SMTP password                                                                          |                   |
| MAIL_PORT               | SMTP port                                                                              |                   |
| MAIL_SERVER             | SMTP mail server                                                                       |                   |
| MAIL_FROM               | Sender address                                                                         |                   |
| MAIL_STARTTLS           | For STARTTLS connections                                                               | `true`            |
| MAIL_SSL_TLS            | For connecting over TLS/SSL                                                            | `false`           |
| MAIL_DEBUG              | SMTP mail debug i.e. whether mail is being debugged or not. Useful during development. | 0                 |
| MAIL_FROM_NAME          | Title for Mail                                                                         |                   |
| MAIL_SUPPRESS_SEND      | whether sending of emails should be suppressed                                         | 0                 |
| MAIL_USE_CREDENTIALS    | whether or not to login to their SMTP server.                                          | `true`            |
| MAIL_VALIDATE_CERTS     | whether to verify the mail server's certificate                                        | `true`            |
| MAIL_TIMEOUT            | timeout in seconds when sending emails                                                 | 60                |

## How to Run

- Clone the repo

```shell
git clone git@github.com:sopherapps/hymns-api.git
```

- Copy `.env.example` to `.env` and update its contents basing on the [settings list](#settings)

```shell
cd hymns-api
cp .env.example .env
```

- Install requirements

```shell
python3 -m venv env 
source env/bin/activate
pip install -r requirements.txt
```

- Run the API app. Ensure it is only one worker so that scdb may function as expected.

```shell
gunicorn -w 1 -k uvicorn.workers.UvicornWorker -b :8000 main:app
```

- Run the CLI app, and see the menu for the different commands

```shell
python manage.py --help
```

- To run tests, stop the app with `Ctrl+C` and run

```shell
pytest
```

## Acknowledgements

- To God, who has created me, chosen me, saved me and sustains me. (Jeremiah 1: 4-5)

## License

Copyright (c) 2023 [Martin Ahindura](https://github.com/Tinitto) Licensed under the [MIT License](./LICENSE)

## Gratitude

> "Sing to the Lord!
>    Give praise to the Lord!
>  He rescues the life of the needy
>    from the hands of the wicked."
>
> -- Jeremiah 20: 13

All glory be to God

<a href="https://www.buymeacoffee.com/martinahinJ" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>
