# README
'app' is a Flask Module.
You would have to setup a python virtual environment to run.
Also, to prevent the accidental change of the database create a local instance of the database.
I've provided a txt file containing the database data.

## Setup
1. Open cmd/terminal in the same folder where the app folder is located
2. Create a vritual environment using the command 

	```
	python -m venv venv 
	```
	or
	```
	python3 -m venv venv
	```
3. Activate the virtual environment
	
	Windows:  
	```
	venv\Scripts\activate
	```
	Linux:	
	```
	source venv/Scripts/activate
	```
4. Your pwd would slightly change
5. Install the dependencies
	```
	pip install flask mysql-connector
	```
	or
	```
	python3 -m pip install flask mysql-connector
	```
6. This will setup your virtual envrionment
7. To get out of the virtual environment just type 
	```
	deactivate
	```
## Setup the Database
1. Dowload the databaseData.txt
2. Create an empty database in your local mysql server
3. If the name of the database is say testDatabase then use command:
	```
	mysql -u root -p testDatabase < databaseData.txt
	```
4. This will create the entire database


## How to Run
1. Before running, set the options corresponding to your local mysql server
2. Go to the file app/__init__.py and change the username, password, and database name
3. Activate the virtual environment
4. Set Flask Options:
	
	Windows : 
	```
	set FLASK_APP=app
	set FLASK_ENV=development
	```
	Linux :   
	```
	export FLASK_APP=app
	export FLASK_ENV=development
	```
5. Run the App:
	```
	flask run
	```
6. This will run a server on your localHost.



## Dependencies
- Flask
- mysql-connector
