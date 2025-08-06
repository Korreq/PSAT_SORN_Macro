Requiremnts:

- Python 3.11 or higher
- DSA Tools psat

Running the Macro:
- Ensure you have the required Python version and DSA Tools installed.
- Make sure the configuration file `config.ini` is set up correctly in configuration folder with the paths to PSAT, model file,input files (if used) and desired output locations.
- Run the macro using this command in sorn_macro directory:
```bash
python scripts\run.py
```

What the Macro does from start to end:

- Modifies the PSAT model based on the configuration settings.
- Calculates the power flow and saves changes as a new temporary model file.
- Filters used elements based on the limits set in configuration or json input file.
- Saves filtered elements to csv files.
- If using input JSON, creates raport file.
- Tries to change the kilovolt values of filtered buses, changing the terminal voltage of connected generators if mvar min and max are different.
- Tries to change transformer current tap.
- Tries to switch shunt status.
- Saves results to specified output directory, with options for timestamping and file naming.
- Creates an info file with details about the run, including configuration settings used.