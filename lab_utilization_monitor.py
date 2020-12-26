'''

This project targets below functions:

1.Check the numbers of login/commits within one week.
2.Check the traffic load
3.Check the control plane load
4.Determine if the device is idle or not:
    if no commit in past 10 days, no traffic, and cpu load is around 99%, determine the device is idle, write into a file



Steps:

1.Device login
2.Check the number of commit within a certain period of time
3.check traffic load
4.check control plane util
5.determine the device utilization
6.Scheduling.==> run the script periodically


'''


from jnpr.junos import Device
from datetime import datetime,timedelta
from collections import namedtuple
import schedule


def device_connection_pyez(ip):
    '''
Use pyez to establish the connection since most of the devices are Junos box

Use namedtuple to save device information

return value is namedtuple.

    '''
    with Device(host=ip,user='labroot',password='lab123') as dev:
        commit_no=commit_no_check(dev)

        traffic_load=traffic_load_check(dev)

        control_util=control_util_check(dev)

        host_name=dev.facts['hostname']


        #return {'commit_no':commit_no,'traffic_load':traffic_load,'control_protocol':control_protocol}
        Device_util=namedtuple('Device', ['host_name','commit_no','traffic_load','control_util'])
        return Device_util(host_name,commit_no,traffic_load,control_util)



def commit_no_check(dev):
    '''
    check the number of commits

    1.get the current date.
    2.Check how many commits are done in the past 10 days.
    '''

    '''
    1.Step 1: get the current date
    
    get the "show system uptime" output via pyez rpc. 
    get rid of "PST" using string split
    
    final format of the current_date_time is 2020-12-25 11:13:48
    
    '''
    current_date_time=dev.rpc.get_system_uptime_information().find('./current-time/date-time').text.split()[:-1]
    current_date=' '.join(current_date_time)

    #print(' '.join(current_date_time))

    '''
    Using datetime lib to locate the previous 10 days
    '''

    ten_days_ago=datetime.fromisoformat(current_date)-timedelta(days=10)
    #print(ten_days_ago)


    '''
    Step 2:, get sys commit history
    
    compare the string of each committed date and ten_days_ago. get the number of commits happened in the past 10
    days
    
    '''

    commit_history=dev.rpc.get_commit_information().findall('commit-history')
    num_of_commit=0
    for commit in commit_history:
        #print(commit.findtext('./date-time'))
        commit_time=' '.join(commit.findtext('./date-time').split()[:-1])
        #print(commit_time)
        if str(commit_time)>str(ten_days_ago):

            num_of_commit+=1

    return num_of_commit



def traffic_load_check(dev):
    '''

    traffic load could be reflected by "show pfe stats traffic

    '''

    input_packets=dev.rpc.get_pfe_statistics().find('pfe-traffic-statistics').findtext('input-pps')
    output_packets=dev.rpc.get_pfe_statistics().find('pfe-traffic-statistics').findtext('output-pps')
    return map(int,[input_packets,output_packets])

def control_util_check(dev):
    '''
    Check Master RE utlization


    '''
    #CPU_IDLE=''

    if dev.facts['2RE'] == True:
        routing_engines = dev.rpc.get_route_engine_information().findall('route-engine')
        for routing_engine in routing_engines:
            if routing_engine.findtext('mastership-state') =='master':
                return routing_engine.findtext('cpu-idle3')
    else:
        routing_engine=dev.rpc.get_route_engine_information().find('route-engine')
        return routing_engine.findtext('cpu-idle3')



def code_interface(file):
    with open(file) as f:
        hosts=f.readlines()
        for host in hosts:
            device_util=device_connection_pyez(host.strip())


            if device_util.commit_no ==0 and sum(device_util.traffic_load)<=5 and int(device_util.control_util)>=99:
                print(f"{device_util.host_name} is idle!! Please release")
            else:
                print(f"{device_util.host_name} is in use!! ")


if __name__=='__main__':

    '''
    Run this script every day/week to confirm utilization of each device. 
    
    Could you python schedule lib or Linux Cronjob.
    
    schedule.every(1).minutes.do(code_interface,'device_list.txt')
    while True:
        schedule.run_pending()
    '''

    code_interface('device_list.txt')