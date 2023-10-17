### Project Set Up
`git clone https://github.com/naiyoma/splice_api`

`cd splice_api`

### Install virtualenv using pip3
`sudo pip3 install virtualenv`
### Create virtualenv
`virtualenv venv`
`virtualenv -p python3 venv` 
`source venv/bin/activate`

### Install project dependencies:
`pip install -r requirements.txt`

### Run the API
`uvicorn main:app --reload`
