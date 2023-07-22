# my_fitbit_dataManager

## Objectives
Collect data from my fitbit account.
2 goals:
* Collect my data, and not rely only of fitbit servers
* process my data the way I want: I tested the advanced services of fitbit, 
and found out I can do the data engineering myself.

I am not trying to manipulate the remote database.

Data processing is done apart with Dataiku.

### Data to monitor
* (done) heart rate time series: intraday
* resting heart rate
* steps
* stairs
* sport => hours
* sleeping hours
* sleeping score

### Data collected
* Activity: Fitbit user's daily activity data
  * step count, distance, elevation, floors, calories burned, active minutes, activity goals, exercise details, etc. The Activity endpoints support returning Intraday data (see Intraday).
  * https://dev.fitbit.com/build/reference/web-api/activity/
  * https://dev.fitbit.com/build/reference/web-api/activity/get-all-activity-types/
  * https://dev.fitbit.com/build/reference/web-api/activity-timeseries/get-activity-timeseries-by-date/
* Heart data
  * https://dev.fitbit.com/build/reference/web-api/heartrate-timeseries/get-heartrate-timeseries-by-date/
* Sleep
  * https://dev.fitbit.com/build/reference/web-api/sleep/get-sleep-log-by-date/

## Principles
```ditaa {cmd=true args=["-E"]}
+--------------+    +----------+    +-------------------------+  
|fitbit servers| -> |py package| -> |tabulated-separated files|  -> dataiku
+--------------+    +----------+    +-------------------------+  
```

## References
___Initial data science article___  
https://towardsdatascience.com/collect-your-own-fitbit-data-with-python-ff145fa10873

___Documentation official web API___  
https://dev.fitbit.com/build/reference/web-api/
https://dev.fitbit.com/build/reference/web-api/help/

___a Fitbit unofficial API___  
https://github.com/orcasgit/python-fitbit

  
https://medium.com/@shsu14/what-i-learned-from-analyzing-my-fitbit-data-61125d85af40  
https://github.com/stephenjhsu/fitbit  
https://python-fitbit.readthedocs.io/en/latest/


## Issues
_Can't connect to HTTPS URL because the SSL module is not available._  
=> install openSSL on Windows

## Web API
___user-id___ 	    The encoded ID of the user. Use "-" (dash) for current logged-in user.  
___base-date___ 	The range start date, in the format yyyy-MM-dd or today.  
___end-date___ 	    The end date of the range.  
___date___ 	        The end date of the period specified in the format yyyy-MM-dd or today.  
___period___ 	    The range for which data will be returned. Options are 1d, 7d, 30d, 1w, 1m.

