# device-utilization-monitoring


This is a quick tool to monitor device utilization. 

In a shared lab environment, engineers need to determine if a lab box is being used for any tasks. 

This quick tool could automate the process with an input file of device IP.


This project targets below functions:

1.Check the numbers of login/commits within one week.
2.Check the traffic load
3.Check the control plane load
4.Determine if the device is idle or not:
    if no commit in past 10 days, no traffic, and idle is around 99%,---> the device is idle



