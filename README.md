Torrent Checker system
======================

## Before First Run
- Create your settings and show list files: [`settings.json`](#settings), [`shows.json`](#torrentList).

Sample files — `settings.json.sample`, `shows.json.sample` — are located in the `default` folder.

## SETTINGS FILE

### Name
- `settings.json`

### Location
- In the root of the torrentChecker folder

### Setup
A sample file is located at: `default/settings.json.sample`
- Copy the file to the root folder (renaming it as needed)
- Open the file in a text editor
- Replace the following with your own values:
    * paths to the folder for downloading torrents
    * paths for logs
    * paths for error messages
    * login credentials for the torrent trackers you use
- Save the file

## SHOW LIST FILE

### Name
- `shows.json`

### Location
- In the root of the torrentChecker folder

##### Each torrent is described by a block like this

```json
{
    "tracker": "tracker_name",
    "hash": "torrent hash",
    "id": "torrent id",
    "description": "your short description"
}
```

##### Field descriptions

* `tracker`
    - Specifies the name of the plugin responsible for the server where the torrent is hosted.
    - Currently supported options:
        + `"tracker" : "rutracker"` - *for [RuTracker.ORG](http://rutracker.org)*
        + `"tracker" : "nnm-club"` - *for [NoNaMe Club](http://nnmclub.to)*

* `hash`
    - System information used to determine whether the torrent has changed since the last download.
    - When adding a new torrent, set an arbitrary value.
        + For example: `"hash" : ""`
    - Afterwards — *DO NOT MODIFY MANUALLY!*
        + **Ex**: `"hash" : "e9c1a82537528e7053659807a002548b"` - *md5 hash of the torrent*

* `id`
    - The ID of the torrent on the tracker.
    - The format of the ID may differ between trackers.
    - For a torrent on [RuTracker.ORG](http://rutracker.org):
        + Topic URL: `http://rutracker.org/forum/viewtopic.php?t=3747359`
        + Torrent ID: `3747359`
        + The line in the file will look like: `"id" : "3747359"`
    - For a torrent on [NoNaMe Club](http://nnm-club.ru):
        + Topic URL: `http://nnmclub.to/forum/viewtopic.php?t=564504`
        + Torrent ID: `564504`
        + The line in the file will look like: `"id" : "564504"`

* `description`
    - A short description to help you identify which torrent you are tracking and what was updated.
    - For example:
        + For the torrent [The Big Bang Theory | Season 6](http://nnmclub.to/forum/viewtopic.php?t=564504)
        + You could write: `TBBT Season 6`
        + The line in the file will look like: `"description" : "TBBT Season 6"`

### Setup
A sample file is located at: `default/shows.json.sample`
- Copy the file to the root folder (renaming it as needed)
- Open the file in a text editor
- Add the list of torrents you want to track
    - *Each torrent block follows the format described [above](#torrentFormat)*
- Save the file

## Plugins

### Twitter Notifications
To use Twitter notifications, the console Twitter client ttytter must be installed and configured.

### Telegram Notifications
To use Telegram notifications:

1. Install [python-telegram-bot](https://github.com/python-telegram-bot).
2. Set the [API token](https://core.telegram.org/bots#6-botfather) of your bot and [your username](https://telegram.org/faq#q-what-are-usernames-how-do-i-get-one) in `settings.json`.
3. Run `python plugins/telegram_notif.py [token] [username]`, substituting the values from above.
4. Send the command `/torrents` to your bot in Telegram.
5. Enter the received `chat_id` in the corresponding field in `settings.json`.

##
*Enjoy using it!*
