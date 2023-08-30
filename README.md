# Azure DevOps Boards Forecast Tool

Generates an Excel file containing a Gantt chart forecasting in which Sprint each Epic and Feature will complete.

The Excel file will list current and future sprints.

## How to use

### config.yaml
Configuration details for each of the classes.
* connections
* default values
* visual formats

### Execution -- generate_forecast.py
Makes calls to the classes to have the forecast Excel file generated.


## Classes
### BoardsApiWrapper
Wrapper functions for the Azure DevOps Boards API.
* Gets Iterations.
* Gets Work Items.

### CustomWorkItemProcessor
Adds custom details to Work Items.
* Calculates Work Remaining.

### Forecaster
Builds the Forecast as an Excel file.

### Constants
Constants classes.
* Azure DevOps terms
* Custom terms
