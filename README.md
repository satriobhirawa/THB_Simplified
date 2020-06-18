# THB_Simplified
THB project using AWS


First of all, we need to install all the requirements from requirements.txt.
Bare in mind that this project is supposed to be initiated in a virtual environment (in this case we are using pipenv) after we install all the requirements. But, we can also upload it into the AWS as well with small changes in our codes.


NOTE on virtual environment: 
- On app.py at line 25 and 26, it requires secret and access key of THB account (where the database is stored).


NOTE on uploading it into AWS:
- Remove the # sign (comment in python) at line 111, 112, and 113
- On app.py at line 25, 26 and 111 it requires secret and access key of THB account (where the database is stored).
- Remove debug=True at line 270
