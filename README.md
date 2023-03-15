# la-dou-backend
La-Dou's backend application built using FASTApi and integrated with MongoDB Atlas

## Getting started with development
1. Clone the repository
2. Create a virtual environment using the command `python -m venv .venv`, preferably using python 3.11
3. Activate the virtual environment using the command `source .venv/bin/activate`
4. Upgrade pip using the command `pip install --upgrade pip`
5. Install the dependencies using the command `pip install -r requirements.txt`
6. Create a file named ".env" to store all Mongo related environment variables. The key value pairs can be found in the group description.
6. Run the application using the command `uvicorn app.main:app --reload`
7. Open the browser and navigate to `http://localhost:8000/docs` for swagger UI.
8. Write code and make pull requests :)

## Contributing
1. Clone the repository
2. Create an issue on Jira or pick one from the backlog
3. Create a new branch using the name specified in the issue
4. The commits should follow the Jira commit message format specified in the issue
5. Push the changes to the remote repository using the command `git push origin <branch-name>`
6. Create a pull request to the `main` branch
7. Wait for the pull request to be reviewed and merged
8. See your changes live on the production server 😎