# Calendar status for Slack
> Updates your Slack status based on your calendar

Using the status from your calendar(s), this app will update your Slack status (e.g. "In a meeting", "On holiday", etc). Currently reads the local Outlook calendar on Windows only, with plans to support O365, Mac, Linux and other non-Outlook apps.
Mimics the functionality of Outlook's Skype for Business addon.

## Installation
Only Windows is currently supported.

Windows:
* Import `task_scheduler_job.xml` to Task Scheduler
* Modify the single action with a path to `pythonw.exe`
    * Argments should be modified to include your personal Slack token and a runtime directory for temp files
* Ensure your Python environment includes the required packages (requirements.txt)

Future versions of this will include an installer.

## Development setup
Written in Python 3.x on Windows.

```
pip install -r requirements.txt
git clone https://github.com/alexluckett/calendar-status-for-slack.git
\path\to\python.exe calendar-status-for-slack\src\main.py --token "YOUR_SLACK_TOKEN" --rundir="\path\to\temp\directory"
```

To force the status to be updated, in the event that your event detection isn't working, add `--force=True` to the command.

## Release History
* 0.0.1
    * Initial version for Outlook 2016 on Windows

## Meta
Alex Luckett – [@alexluckett](https://twitter.com/alexluckett)

Distributed under the MIT license. See ``LICENSE`` for more information.

[https://github.com/alexluckett/calendar-status-for-slack](https://github.com/alexluckett/calendar-status-for-slack)

## Contributing
1. Fork it (<https://github.com/alexluckett/calendar-status-for-slack>)
2. Create your feature branch (`git checkout -b feature/foo-bar`)
3. Commit your changes (`git commit -am 'Add some foo-bar'`)
4. Push to the branch (`git push origin feature/foo-bar`)
5. Create a new Pull Request
