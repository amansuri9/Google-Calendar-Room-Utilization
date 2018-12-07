# README #

### About this project ###
University Facilities Information (UFI) and OIT are collaborating on a summer project to create a utilization report for room resources within Google Calendar. In short, we are attempting to better understand how our conference rooms are used across campus. We believe this data can help inform both strategic decision making at the University level as well as tactical, day-to-day management of specific conference rooms within buildings and departments.

* Version 0.0.1

### How do I get set up? ###

#### Requirements  ####

Python 3.6.5  
Bitbucket  
Packages  
Credentials  

#### Getting Started ####

###### Python ######
To verify the correct Python version, run the following:  
`$ python --version`  
The Python version should be 3.6.5

###### Git ######
To check if you have git installed, run the command:  
`$ git -- version`   
Once git has been installed, you can make a folder to hold the project. Run the following which will create a directory called GoogleCalendar  
`$ mkdir GoogleCalendar`  
To move into the GoogleCalendar directory, type:  
`$ cd GoogleCalendar`  
You will see a confirmation that the repository was initialized.  
To set the URL of where the project is remotely located, type:  
`$ git init`  
`$ git remote add origin https://github.com/amansuri9/Google-Calendar-Room-Utilization.git`  
To pull the branch of the project, type:  
`$ git pull origin FinalCleanUp`  
If it is location inside a private repository, you will be asked to enter a username and password. Please do so appropriately.  

###### Packages ######
Once you have all the files in your local repository, install the required packages by executing the following command:  
`$ pip install -r requirements.txt`  

###### Credentials ######
In order to run the file, you need the indicated JSON file called "clientsecret" which grants the google credentials. This account grants access to productions. This currently runs on google_cal_space.py
Meanwhile "client_secret" is the JSON file for the testing environment. This currently runs for groups.py.  


#### How to run tests  ####
#### Deployment instructions ####
Python scripts  
Assortment of scripts that run on the command line, i.e. Terminal on Mac OS X, and Command Prompt on Windows.  
`google_cal_space.py, funtions.py, groups.py`  
Run the following file to retrieve information on the rooms and events in Google Calendar, specifying the start and end date. The events on the start date are included and the events on the end date are not included:  
`$ python google_cal_space.py -s YYYY-MM-DD -e YYYY-MM-DD`  
This outputs four files: rooms.csv, events.csv, invitee.csv, and invitee_aggregate.csv.   
##### rooms.csv #####
This is a csv file that contains information on the space's capacity, name, category, building numbers, space numbers, and the space ID in email and number formats.  
##### events.csv #####
This contains information about the events from each room.   
It prints out the event name, event id, attendees, start date, start time, end time, and the meeting's visibility.  
##### invitee.csv #####
This is a csv file merged from the events.csv with the attendees of the events. This expands the attendees column in the events.csv file and outputs the nested information.  
This file is also merged with the rooms.csv file to contain the information of the particular room when an event is occurring. It displays the attendee of each event per row.  
It prints out the event name, event id, the meeting's visibility, the event's start date, the start time, the end time, the space email, the space capacity, the space name, the space id, the building and space number, and the invitees with their response status.  
##### invitee_aggregated.csv #####
This is a csv file derived from the invitee.csv containing the same information. It's only difference is that it displays the response status of the event per row.  
The last file called invitee_aggregated is the final output. It displays the event summary, event id, start date, end date, space email, space capacity, space name, space category, the building and space number, space id, the number of attendees, and the response of each attendee.  
It prints out the event name, event id, the meeting's visibility, event start date, the start time, the end time, the space email, the space capacity, the space name, and id, the building and space number, and the response status of the event per row.  
The difference between invitee.csv and invitee_aggregated.csv is that invitee_aggregated.csv groups the invitees by response status and diplays each response status of the event per row.  
Run the following file to retrieve information on the groups in Google Calendar:  
`$ python groups.py`  
This outputs three files: groups, members, and groups_and_members.  
##### groups.csv #####
This outputs the group count, group email, group id, group name, and non-editable aliases.  
##### members.csv #####
This outputs the member's email, group id, member id, and the member's status in the group.
##### groups_and_members #####
This is a merging of the two csv files above that outputs the member email, groupid, member id, status, group email, name, and noneditable aliases.   
This outputs the member's email, group id, member's id, group member status, the group email, the group name, and the non-editable aliases.   
