# <p align="center"> Youtube Helper </p>
![GitHub last commit (branch)](https://img.shields.io/github/last-commit/JacobW22/Youtube_helper_project/main?style=flat-square&logo=github&color=blue)
![GitHub repo size](https://img.shields.io/github/repo-size/JacobW22/Youtube_helper_project?style=flat-square&color=lightblue)
[![CodeQL](https://github.com/JacobW22/Youtube_helper_project/workflows/CodeQL/badge.svg)](https://github.com/JacobW22/Youtube_helper_project/actions?query=workflow%3ACodeQL)
[![Django CI](https://github.com/JacobW22/Youtube_helper_project/actions/workflows/django.yml/badge.svg)](https://github.com/JacobW22/Youtube_helper_project/actions/workflows/django.yml)

> Youtube Helper is an application that offers free tools operating on Youtube data

<!-- > Live demo [_here_](http://165.232.68.73:8000). -->

## Table of Contents
* [General Info](#general-information)
* [Technologies Used](#technologies-used)
* [Features](#features)
* [Screenshots](#screenshots)
* [Setup](#setup)
* [Project Status](#project-status)
* [Contact](#contact)


## General Information
- The application offers such tools as:<br>
    - Video downloader including multiple formats<br>
    - Filtering comments attached with sorting and searching phrases<br>
    - Transferring youtube playlists to spotify account<br>
    - AI powered avatar generator

- You have an overview of the history of your activities and the ability to customize your account settings
- You can access and use free api of the application to get your history data
- The application uses a message broker for scheduling long-running tasks such as generating playlist or sending user's avatars to aws bucket

## Technologies Used
- Python - v3.10.0
- Django - v4.2.4
- Django Rest Framework - v3.14.0
- Bootstrap - v5.2.2
- JQuery - v3.2.1
- Celery - v5.3.1 and Rabbitmq - v3.12.2
- Docker - v23.0.5
- AWS S3 buckets


## Features
- You can create accounts and manipulate over user settings
- You can use free tools including api service
- You can check your recent activity and go back to items in history
- You can manipulate your downloads, searching, transferring history, etc.
- You can change user information such as: Username, E-mail, Password
- All created avatars are stored in S3 bucket
- Working password resetting system


## Screenshots
![Example screenshot](app/static/images/example_screenshot1.png)
![Example screenshot](app/static/images/example_screenshot2.png)
![Example screenshot](app/static/images/example_screenshot3.png)
![Example screenshot](app/static/images/example_screenshot4.png)
![Example screenshot](app/static/images/example_screenshot5.png)


## Setup
If you want to open project locally: 

```
(on Windows, Linux, MacOS)
NOTE: SET UP ENVIRONMENT VARIABLES FIRST INTO THE .ENV FILE

cd into the main directory then:

- Without AWS setup
$ docker compose build
$ docker compose up

-With AWS setup
$ docker compose -f prod.yml build
$ docker compose -f prod.yml up
```

## Project Status
_working on_


## Contact
Created by [@Jacob](mailto:jwis02202@gmail.com) - feel free to contact me!
