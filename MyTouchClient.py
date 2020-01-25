import socket
import time
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("hostIP", help='Rinnai Touch Host IP address')

# Must be one of these
parser.add_argument("--mode",choices=['heat','evap','cool','rc'], help='What function are we acting on')
parser.add_argument("--action",choices=['on','off'], help='What are we doing to the mode')

parser.add_argument("--heatTemp",type=int,choices=range(20,30))
parser.add_argument("--heatZone",choices=['A','B','C','D'], help='Which Zone?')
parser.add_argument("--zoneAction",choices=['on','off'], help='What are we doing to the zone')
parser.add_argument("--heatFan",choices=['on','off'], help='Turn the Heater circulation fan on/off')

parser.add_argument("--coolTemp",type=int,choices=range(8,30))
parser.add_argument("--coolZone",choices=['A','B','C','D'], help='Which Zone?')
parser.add_argument("--coolFan",choices=['on','off'], help='Turn the Cooling circulation fan on/off')

parser.add_argument("--evapFanSpeed",type=int,choices=range(1,16))
parser.add_argument("--evapPump",choices=['on','off'], help='Turn the Evap pump on/off')
parser.add_argument("--evapFan",choices=['on','off'], help='Turn the Evap fan on/off')

args = parser.parse_args()

print(args)

# Touch Box IP address
port = 27847
touchIP = args.hostIP

# create an ipv4 (AF_INET) socket object using the tcp protocol (SOCK_STREAM)
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# connect the client
print("Connecting ...")
client.connect((touchIP, port))
time.sleep(0.2)
response = client.recv(4096)
print(response)

# setup some basic commands
# Top level mode
# Operating mode
modeCoolCmd = 'N000001{"SYST": {"OSS": {"MD": "C" } } }'
modeEvapCmd = 'N000001{"SYST": {"OSS": {"MD": "E" } } }'
modeHeatCmd = 'N000001{"SYST": {"OSS": {"MD": "H" } } }'

# Heating Commands
#heatCmd = 'N000001{"HGOM": {"OOP": {"ST": "{}" } } }' # N = On, F = Off
heatOnCmd = 'N000001{"HGOM": {"OOP": {"ST": "N" } } }'
heatOffCmd = 'N000001{"HGOM": {"OOP": {"ST": "F" } } }'

heatSetTemp = 'N000001{{"HGOM": {{"GSO": {{"SP": "{temp}" }} }} }}'
heatCircFanOn = 'N000001{"HGOM": {"OOP": {"ST": "Z" } } }'

#heatZone = 'N000001{"HGOM": {"Z{zone}O": {"UE": "{}" } } }'  # Y = On, N = Off
heatZoneOn = 'N000001{{"HGOM": {{"Z{zone}O": {{"UE": "Y" }} }} }}'
heatZoneOff = 'N000001{{"HGOM": {{"Z{zone}O": {{"UE": "N" }} }} }}'
heatZoneA = 'N000001{"HGOM": {"ZAO": {"UE": "{}" } } }'  # Y = On, N = Off
heatZoneB = 'N000001{"HGOM": {"ZBO": {"UE": "{}" } } }'
heatZoneC = 'N000001{"HGOM": {"ZCO": {"UE": "{}" } } }'
heatZoneD = 'N000001{"HGOM": {"ZDO": {"UE": "{}" } } }'

# Cooling Commands
#coolCmd = 'N000001{"CGOM": {"OOP": {"ST": "{}" } } }' # N = On, F = Off
coolOnCmd = 'N000001{"CGOM": {"OOP": {"ST": "N" } } }'
coolOffCmd = 'N000001{"CGOM": {"OOP": {"ST": "F" } } }'

coolSetTemp = 'N000001{{"CGOM": {{"GSO": {{"SP": "{temp}" }} }} }}'
coolCircFanOn = 'N000001{"CGOM": {"GSO": {"FS": "M" } } }'

#coolZone = 'N000001{"HGOM": {"Z{zone}O": {"UE": "{}" } } }'  # Y = On, N = Off
coolZoneOn = 'N000001{{"CGOM": {{"Z{zone}O": {{"UE": "Y" }} }} }}'
coolZoneOff = 'N000001{{"CGOM": {{"Z{zone}O": {{"UE": "N" }} }} }}'
coolZoneA = 'N000001{"CGOM": {"ZAO": {"UE": "{}" } } }'  # Y = On, N = Off
coolZoneB = 'N000001{"CGOM": {"ZBO": {"UE": "{}" } } }'
coolZoneC = 'N000001{"CGOM": {"ZCO": {"UE": "{}" } } }'
coolZoneD = 'N000001{"CGOM": {"ZDO": {"UE": "{}" } } }'

# Evap Cooling commands
#evapCmd =  'N000001{"ECOM": {"GSO": {"SW": "{}" } } }' # N = On, F = Off
evapOnCmd =  'N000001{"ECOM": {"GSO": {"SW": "N" } } }'
evapOffCmd =  'N000001{"ECOM": {"GSO": {"SW": "F" } } }'

#evapPumpCmd = 'N000001{"ECOM": {"GSO": {"PS": "{}" } } }' # N = On, F = Off
evapPumpOn = 'N000001{"ECOM": {"GSO": {"PS": "N" } } }'
evapPumpOff = 'N000001{"ECOM": {"GSO": {"PS": "F" } } }'

#evapFanCmd = 'N000014{"ECOM": {"GSO": {"FS": "{}" } } }' # N = On, F = Off
evapFanOn = 'N000014{"ECOM": {"GSO": {"FS": "N" } } }'
evapFanOff = 'N000014{"ECOM": {"GSO": {"FS": "F" } } }'
evapFanSpeed = 'N000001{{"ECOM": {{"GSO": {{"FL": "{speed}" }} }} }}' # 1 - 16

def SendToTouch(client,cmd):
    """Send the command and return the response."""
    print("DEBUG: {}".format(cmd))
    response = "NA"
    client.send(cmd.encode())
    response = client.recv(4096)
    return response

def HandleMode(args,client):
    """Process setting mode and its state."""
    if args.mode == "heat":
        # Make sure we are in heater mode
        resp = SendToTouch(client,modeHeatCmd)
        print(resp)
        # Give it a chance if there are further commands
        time.sleep(2)

        if args.action is not None:
            if args.action == "on":
                resp = SendToTouch(client,heatOnCmd)
                print(resp)
            else:
                # Assume it is off cmd then
                # Assume we are in heater mode, otherwise no need to turn it Off
                resp = SendToTouch(client,heatOffCmd)
                print(resp)
                return

        if args.heatTemp is not None:
            # Assume on already
            resp = SendToTouch(client,heatSetTemp.format(temp=args.heatTemp))
            print(resp)

        if args.heatZone is not None:
            if args.zoneAction == "on":
                # Assume on already
                resp = SendToTouch(client,heatZoneOn.format(zone=args.heatZone))
                print(resp)
            elif args.zoneAction == "off":
                resp = SendToTouch(client,heatZoneOff.format(zone=args.heatZone))
                print(resp)
                return

    elif args.mode =="cool":
        # Make sure we are in cooling mode
        resp = SendToTouch(client,modeCoolCmd)
        print(resp)
        # Give it a chance if there are further commands
        time.sleep(2)

        if args.action is not None:
            if args.action == "on":
                resp = SendToTouch(client,coolOnCmd)
                print(resp)
            else:
                # Assume it is off cmd then
                # Assume we are in cooling mode, otherwise no need to turn it Off
                resp = SendToTouch(client,coolOffCmd)
                print(resp)
                return
        
        if args.coolTemp is not None:
            time.sleep(2)
            # Assume on already
            resp = SendToTouch(client,coolSetTemp.format(temp=args.coolTemp))
            print(resp)

        if args.coolZone is not None:
            time.sleep(2)
            
            if args.zoneAction == "on":
                # Assume on already
                resp = SendToTouch(client,coolZoneOn.format(zone=args.coolZone))
                print(resp)
            elif args.zoneAction == "off":
                resp = SendToTouch(client,coolZoneOff.format(zone=args.coolZone))
                print(resp)
                return

    elif args.mode =="evap":
        # Make sure we are in evap mode
        resp = SendToTouch(client,modeEvapCmd)
        print(resp)
        # Give it a chance
        time.sleep(2)

        if args.action is not None:
            if args.action == "on":

                resp = SendToTouch(client,evapOnCmd)
                print(resp)
            else:
                # Assume it is off cmd then
                # Assume we are in heater mode, otherwise no need to turn it Off
                resp = SendToTouch(client,evapOffCmd)
                print(resp)
                return

        if args.evapFanSpeed is not None:
            resp = SendToTouch(client,evapFanSpeed.format(speed=args.evapFanSpeed))
            print(resp)

        if args.evapFan is not None:
            if args.evapFan == "on":
                resp = SendToTouch(client,evapFanOn)
                print(resp)
            else:
                # Assume off cmd then
                resp = SendToTouch(client,evapFanOff)
                print(resp)
        
    else:
            print("Not implemented yet")

if args.mode is not None:
    HandleMode(args,client)
else:
    exit()

client.close()