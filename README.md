# Lapup-Air-Quality-sites


Downloads sensors data using [PurpleAir HTTP API](https://api.purpleair.com/).

Applied correction factor on quality controlled sensors data.

Plots last 24 hours and last week timeseries.

Plots last values on google map. Markers are colored according Air Quality Index.

Uploads list of files to FTP server, preserving folder structure.

To avoid overlapping cron job execution, use flock in crontab:

```
*/15 * * * * /usr/bin/flock -w 0 ~/lapup_air_quality_sites.lock python3 ~/Lapup-Air-Quality-sites/main.py
```