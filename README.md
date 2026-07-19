# Solo Leveling Web App
Manually customise your quests. Complete them and become the next King!

## App running guideline
**1. Setting up virtual environment**
At where you place your folder, run `python -m venv venv` and wait for a few minutes for environment setup.

**2. Installing dependency**
Once the `venv/` folder appears, the virtual environment is good to go. This app utilises **Flask** library as its frontend, so perform `pip install flask` is essential.

**3. Deploying the app**
- Once set, run `python3 app.py` on the terminal. The default port is *9090* and can be customised anytime.
- The web app can be accessed locally at `http://127.0.0.1:<port>`.
- All data is stored locally in the file `curr_data.json`, so the next time you start the app, your progress won't get lost!
- To reset your progress, simply remove the JSON file `curr_data.json`.

***Important Note***: Remember to `deactivate` the virtual environment when you stop tracking!!!

Enjoy the journey to become the better version of yourself!!!

# Update History
- **v1.0.0**: Initial Release.
- **v1.1.0**: Added *Tier-Ranking System* and *Completed Quests* page.
- **v1.1.1**: Added `datetime` module to support timestamp logging for **Completed Quests** page.
- **v2.0.0**: Added *Achievement System* and restructure the app.