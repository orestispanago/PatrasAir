# PatrasAir


Downloads sensors data using [PurpleAir HTTP API](https://api.purpleair.com/).

Applies correction factor on quality controlled sensors data.

Plots last 24 hours and last week timeseries.

Plots last values on google map. Markers are colored according Air Quality Index.

Uploads image files to FTP server.

To avoid overlapping cron job execution, use flock in crontab:

```
*/20 * * * * /usr/bin/flock -w 0 ~/patrasair.lock python3 ~/PatrasAir/main.py
```