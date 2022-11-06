# CrowdInvest

**CrowdInvest** is an Egyptian for-profit crowd funding platform that allows people to raise money or donate for campaigns with different categories ranging from

**Emergency** Fire Tragedy Earthquake Flood Storm Tornado Nonprofit **Education** College tuition Classroom Computer Study abroad **Medical** Cancer IVF Leukemia Lymphoma Health insurance Breast cancer Surgery

The project is developed using **Python**, **Django** framework .

## Table of Contents

---

<!-- TOC -->

- [Features](#features)
- [Getting Started](#getting-started)
  - [Setup Your Environment](#setup-your-environment)
- [Configurations](#configurations)
- [Dependencies](#dependencies)
  <!-- /TOC -->

## Features

---

- Sign in with your Facebook account
- get Facebook profile picture adn email
- Create a fund raising campaign
- Report campaigns
- Rate campaigns
- Add comments to any campaign
- Reply to comments
- Report comments
- View all your campaigns and donations
- Live search for campaigns
- Browse campaigns based on category

## Getting Started

---

To use and run this project you need to:

Before executing the following commands, please install python 3 as stated in the following setup

#### Setup Your Environment

---

1. Run the following command to install the project locally assuming windows environment.

**Open your windows terminal and type**

```bash
python -m pip install --upgrade pip

git clone https://github.com/mohamadbakri/crowd-invest-django.git

cd crowd-invest-django/

python -m venv .venv

.\.venv\Scripts\activate

pip install -r requirements.txt
```

2. Execute configuration required in configurations section

```bash
python manage.py makemigrations project account

python manage.py migrate
```

5. Run the server

```
python manage.py runserver_plus --cert-file cert.crt
```

6. Go to the browser and go to the following url: **https://mysite.com:8000**

##### Note:

**Make sure to edit your hosts file in windows.** <br/>By editing the hosts file, specifically adding a custom IP address that points to your domain,<br/> you’ll be able to open your website.<br/>This is useful if you want to modify your site after migrating and see how it’ll look on the new server. **Change the File Manually** <br/>1- Press Start and find Notepad. Right-click to Run as administrator. <br/>2- Once in Notepad, go to **File -> Open.** Get to **C:\Windows\System32\Drivers\etc** and make sure to select **All Files** to find the **hosts** file. <br/>3- Now you can edit the hosts file. Add the custom **IP address** you’ve made earlier, followed by a **space**, then your **domain name.** In our case we have to add

**127.0.0.1 mysite.com**

at the end of the hosts file and save.

For linuxt simply open your terminal and type **sudo vim /etc/hosts** and add **127.0.0.1 mysite.com** at the end of the file and save

## Dependencies

---

- [python 3.6 or later](https://www.python.org/download/releases/3.0/)
