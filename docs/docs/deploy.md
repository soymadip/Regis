---
title: Deployment
icon: lucide/rocket
---

!!! bug "Development stopped"

    - Pyrogram is no longer maintained; Regis uses its Kurigram-compatible API.
    - Also this was my 1st project, code is messy. So porting will be extremely time consuming.

## Deploy Methods

=== "Local MongoDB with Docker Compose"

    1. Copy the database example environment file and change the password:

        ```bash
        cp .env.docker.example .env.docker
        ```

    2. Start MongoDB:

        ```bash
        docker compose --env-file .env.docker up -d mongodb
        ```

    3. Set the matching `DATABASE_URI` and `DATABASE_NAME` values in the bot's `.env` file, then follow the local installation steps below.

    Stop the database with `docker compose --env-file .env.docker down`. Add `-v` only when you intentionally want to delete the MongoDB data volume.

<!--     1. Install Docker or Podman.

    2. Get the `.env` file

        ```bash
        curl -L https://soymadip.github.io/Regis/env -o .env
        ```
    3. Edit `.env` file with required options. See below for more config options.

        ```bash
        nano .env
        ```
    3. Pull official docker image:

        ```bash
        docker pull soymadip/regis:latest
        ```
    4. Run The container with the `.env` file:

        ```bash
        docker run -d --env-file .env --name Regis-bot soymadip/regis:latest
        ```
 -->

=== "To VPS or Local"

    1. Clone Repo:
        ```bash
        git clone https://github.com/soymadip/Regis
        ```
    2. Get the `.env` file

        ```bash
        curl -L https://soymadip.github.io/Regis/env -o .env
        ```
    3. Edit `.env` file with required options. See below for more config options.

        ```bash
        nano .env
        ```
    4. Install Packages

        ```bash
        uv sync
        ```
    5. Run Regis

        ```bash
        uv run regis
        ```

=== "To Heroku"

    You can quickly deploy Regis to Heroku using the below button.  

    [![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/soymadip/Regis.git)

    Configuration options can be found below.

---

## :octicons-gear-16: Configuration Options

Below are the available configuration variables/options & their descriptions:

!!! info

    Default values can be found [here](https://github.com/soymadip/Regis/blob/main/regis/info.py#L17).


### Bot Credentials

| **Variable**   | **Description**                                                                                           | **Required** |
|----------------|----------------------------------------------------------------------------------------------------------|:--------------:|
| **BOT_TOKEN**  | Create a bot using [@BotFather](https://telegram.dog/BotFather) & get the Telegram API token.             | Yes          |
| **API_ID**     | Get this value from [telegram.org](https://my.telegram.org/apps).                                         | Yes          |
| **API_HASH**   | Get this value from [telegram.org](https://my.telegram.org/apps).                                         | Yes          |


### User & Admin

| **Variable**      | **Description**                                                                                | **Required** |
|-------------------|-----------------------------------------------------------------------------------------------|:--------------:|
| **ADMINS**        | Username or ID of the admin(s). Separate multiple admins by space.                             | Yes          |
| **AUTH_USERS**    | Restricts the use of inline queries to specified users. Add user IDs separated by space.       | Yes          |
| **CHANNELS**      | Username or ID of channels/groups from which to save media for the DB. Separate multiple IDs by space. | Yes          |
| **AUTH_CHANNEL**  | ID of channel for forced subscription.<br> Users must join this channel to use the bot.        | No           |
| **AUTH_GROUPS**   | Group IDs for authentication purposes. Format: space-separated integers.                       | No           |
| **UPSTREAM_REPO** | If you want to use a customized fork, set this variable to the GitHub URL of your fork.        | No           |
| **MAINTENANCE_MODE** | Set to `True` or `False`.<br> If `True`, the bot will operate in maintenance mode.          | No           |


### DB & Storage

| **Variable**             | **Description**                                                                                         | **Required** |
|--------------------------|--------------------------------------------------------------------------------------------------------|:--------------:|
| **DATABASE_URI**         | [MongoDB](https://www.mongodb.com) URI. Get this from your MongoDB dashboard or connection string.      | Yes          |
| **DATABASE_NAME**        | Name of the database in [MongoDB](https://www.mongodb.com).                                             | Yes          |
| **COLLECTION_NAME**      | Name of the collection. Use different collection names for each bot if sharing a database.              | Yes          |
| **LOG_CHANNEL**          | A channel ID to log the activities of the bot. Make sure the bot is an admin in the channel.            | Yes          |
| **FILE_STORE_CHANNEL**   | Channel ID(s) where file store links of posts should be made. Separate multiple IDs by space.           | Yes          |
| **PUBLIC_FILE_STORE**    | Set to `True` or `False`.<br> If `False`, your bot cannot be used as a file storage bot by others.      | No           |
| **PROTECT_CONTENT**      | Set to `True` or `False`.<br> If `True`, files from the bot cannot be forwarded to any chat.            | No           |
| **INDEX_REQ_CHANNEL**    | Channel ID where index requests are sent. Defaults to LOG_CHANNEL if not specified.                     | No           |
| **CACHE_TIME**           | Time in seconds for caching inline query results. Default is 300.                                       | No           |
| **SESSION**               | Name for the Kurigram session. Default is 'Regis'.                                                     | No           |


### Bot Settings

| **Variable**              | **Description**                                                                                                 | **Required** |
|---------------------------|----------------------------------------------------------------------------------------------------------------|:--------------:|
| **CAPTION_FILTER**        | Set to `True` or `False`.<br> When enabled, the bot will also match search terms in file captions.              | No           |
| **SUPPORT_CHAT**          | Username or link of your support chat (without @) where Users will be directed here for help.                   | No           |
| **PICS**                  | Telegraph links of images to show in the start message. Multiple images can be used, separated by spaces.       | No           |
| **P_TTI_SHOW_OFF**        | Set to `True` or `False`.<br> If `True`, users will be redirected to send `/start` to the bot's PM else, files will be sent directly to users' PM. | No |
| **IMDB**                  | Set to `True` or `False`.<br> Enable or disable IMDB data in search results.                                    | No           |
| **LONG_IMDB_DESCRIPTION** | Set to `True` or `False`.<br> If enabled, the long IMDB story will be used instead of short desc.               | No           |
| **IMDB_TEMPLATE**         | Custom template for displaying IMDB data.<br> Available fields depend on movie metadata.                        | No           |
| **SPELL_CHECK_REPLY**     | Set to `True` or `False`.<br> If enabled, the bot will suggest related files whenever message is posted in grp. | No           |
| **SINGLE_BUTTON**         | Set to `True` or `False`.<br> If `True`, file name & file size will be shown in a single button instead of 2 separate buttons. | No|
| **CUSTOM_FILE_CAPTION**   | Custom caption template for files.<br> Available variables: `{file_name}`, `{file_size}`, `{file_caption}`.     | No           |
| **BATCH_FILE_CAPTION**    | Custom caption template for batch files.<br> If not set, will use CUSTOM_FILE_CAPTION instead.                  | No           |
| **MAX_LIST_ELM**          | Maximum number of elements to show in lists like cast, genre etc. Integer value (e.g., 10).                     | No           |
| **WELCOM_NEW_USERS**      | Set to `True` or `False`.<br> If `False`, the bot will not welcome new users in groups.                         | No           |
| **WELCOM_NEW_TEXT**       | Custom welcome message for new users. Available variables: `{mention}`, `{chat}`.                               | No           |
| **IGNORE_WORDS**          | Words to ignore in search queries. Separate multiple words with `|` (pipe symbol).                              | No           |
| **CUSTOM_FOOTER**         | Custom footer text to be displayed in messages.                                                                 | No           |
| **PM_FILTER**             | Set to `True` or `False`.<br> If `True`, enables filtering in private messages.                                 | No           |
|**AUTO_MESSAGE_DELETE_TIME** | Time in seconds after which bot messages are auto-deleted. Set to 0 to disable.                               | No           |
