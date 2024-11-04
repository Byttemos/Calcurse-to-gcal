# DISCLAIMER!

This repository is under development, and the code is borderline useless at this point! Please check back later!

# Introduction

Synchronizing calcurse calendar events with google calendar made easy (sort of).

## Features

- Automatically checks for local calendar changes, and writes them to google cloud
- Automatically reads google calendar entries into local calendar on startup
- That's about it

## Requirements

### Calcurse
Calcurse is a TUI calendar available on most distros. I trust you can find installation instructions elsewhere.

### Google developer console
There are a few hoops to jump through to get this to work in terms of google calendar's API. I followed this guide for starters:
https://medium.com/@ayushbhatnagarmit/supercharge-your-scheduling-automating-google-calendar-with-python-87f752010375
The observant individuals will notice a lot of the code from this guide looks similar to mine, and that's because it is. However, it has been modified to automate synchronization, and read the cursecal calendar entries.

