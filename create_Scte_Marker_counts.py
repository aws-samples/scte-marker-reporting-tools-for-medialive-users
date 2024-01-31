#!/usr/local/bin/python3
#  a simple CW dashboard maker for Elemental MediaLive SCTE marker counts
#  call this script directly with command:  python3 -c "$(curl -fsSL 'https://raw.githubusercontent.com/robclemamzn/SCTE_Reporting_Tools/main/create_Scte_Marker_counts.py')" 

#
import os
import json
from json import JSONEncoder
import code
import time
import copy
from time import gmtime, strftime
import datetime
from datetime import datetime
import subprocess 
#------------------------------------------------------------------------------------
thisversion = "2"
tyellow="\033[1;33;40m"
tnormal="\033[0;37;40m"
CEND ='\33[0m'
CYELLOW ='\33[33m'
CRED  ='\33[31m'
CWHITE  ='\33[37m'

# -- widget template ---

MarkerCounts_widet_d = {
            "type": "log",
            "x": 0,
            "y": 0,
            "width": 24,
            "height": 10,
            "properties": {
                "query": "SOURCE 'ElementalMediaLive' | parse channel_arn \"*:*:*:*:*:*:*\" as z1,z2,z3,REGION,ACCT,z4,CHL\n| filter CHL=999999 \n| filter @message like \"Clock=\"\n| parse @message /(?<CLK1>Clock=....{12}.....)/\n| parse CLK1 '*=*]' as z5, PROCESS\n| fields (strcontains(@message, \"IngestM2TS\") as CUESINGESTED\n| fields (strcontains(@message, \"OutputContentM2TS\") as OUTPUT_CUES_IN_RTP\n| fields (strcontains(@message, \"OutputPlaylistHLS\") as OUTPUT_CUES_IN_M3U8\n| stats sum(CUESINGESTED) as Cues_Ingested, sum(OUTPUT_CUES_IN_RTP) as Cues_Sent_RTP, sum(OUTPUT_CUES_IN_M3U8) as Cues_sent_HLS by bin (1hr)",
                "region": "xxx",
                "title": "SCTE Marker counts by hour",
                "view": "timeSeries",
                "stacked": "false"
            }
}

#----------------------------------------------------------------------------------------------------
WidgetsList = [MarkerCounts_widet_d]
RTPWidgetsList=[]
#----------------------------------------------------------------------------------------------------

def GetCLIResult(mycmd):
        try:
                result = subprocess.run(mycmd, stdout=subprocess.PIPE)
                DecodedReply = json.loads(result.stdout.decode('utf-8'))
                return(DecodedReply)
        except:
                print("Could not get valid CLI resonse to cmd: ",mycmd, "...Please report this error to the author. Exiting.")
                exit()
#-------------------------------------------------------------------------------------------------------
tnow = datetime.now()
tstamp = tnow.strftime("%m%d%y_%H%M%S")
#-------------------------------------------------------------------------------------
quote='"'
print(CWHITE)
print("\n","========== WELCOME TO THE SCTE MARKER DASHBOARD MAKER v",thisversion," ============", CEND)
print("   This script makes a Dash for:  MediaLive SCTE Marker Counts per hour")
print(CRED)
print(CRED,"   NOTE 1:",CEND," Some ad breaks might span top-of-hour.")
print(CRED,"   NOTE 2:",CEND," Each HLS output variant gets copies of markers.")
print(CRED,"   NOTE 3:",CEND," Some CUE-OUT markers use auto-return without any corresponding ingested CUE-IN.")
print(CEND)
print("\n\n")
#--------------------------------------------------------------------------
RunMode = "s"
##--------------------------------------------------------------------------------------
AllCannelsJSON_d = {'Channels': [{}]}  ## empty dictionaries for all channels and target channels
TargetChannelsJSON_d= {'Channels': []}
##
cmd = ['/usr/local/bin/aws','--no-paginate','medialive','list-channels']
try:
	AllCannelsJSON_d = GetCLIResult(cmd)
except:
	print("!! No valid reply from list-channels call. Sorry!!  --> Exiting .")
	exit()

ChCount = len(AllCannelsJSON_d['Channels'])
if (ChCount == 0 ):
	print("---> No Channels found for this Account in this region; exiting.")
	exit()	
		
##------------------------------------------------------------------------------------
if RunMode == 's' :
	print("\n\n")
	print("--> Scanning channels in this AWS account...","\n\n")
	print("\n\n",CWHITE,"This account has the following channels defined:")	
	print("  ","NAME","                                               ","ID", CEND)
	for ChIndex in range (0, ChCount):  ## now we list all the chx
		chName = (AllCannelsJSON_d['Channels'][ChIndex]['Name'])
		chName = chName.ljust(45, ' ')
		chanID = (AllCannelsJSON_d['Channels'][ChIndex]['Id'])
		print("  ",chName, "      ",chanID)
	
	print("\n",CWHITE)
	
	SingleCh = input("--> Specify (copy+paste) the Channel ID to use: ")
	print(CEND)
	
	validID = False
	for ChIndex in range (0, ChCount):
		if (SingleCh == AllCannelsJSON_d['Channels'][ChIndex]['Id']):
			validID = True
			break
		
	if (validID):
		print("") 
	
	else:
		print("Specified ID",CRED, SingleCh,CEND,"doesn't appear to be a Channel ID. Exiting.","\n\n")
		exit()
	
	for ChIndex in range (0, ChCount):  
		ChPointer = AllCannelsJSON_d['Channels'][ChIndex]
		if (SingleCh == ChPointer['Id'] ):
			print("----> Adding single channel",ChPointer['Name'])
			
			TargetChannelsJSON_d['Channels'].append(ChPointer)
			break
		else:
			print(".", end="")
	
# ------------------------------------------------------------------------------------
myregion = "us-east-1"
ChCount = len(TargetChannelsJSON_d['Channels'])
MetricTemplateLine = [ "...", "nextchannelID", "Pipeline", "nextpipevalue", { "label": "labelvalue" } ]
quote='"'
TotalPipelines = -1
# ------------------------------------------------------------------------------------
NeedsRTPWidget = 0
TotalRTPWidgets=0
#
for ChIndex in range (0, ChCount):
	chName = ""
	MetricTemplateLine = [ "...", "nextchannelID", "Pipeline", "nextpipevalue", { "label": "labelvalue" } ]
	chName = (TargetChannelsJSON_d['Channels'][ChIndex]['Name'])
	chanID = (TargetChannelsJSON_d['Channels'][ChIndex]['Id'])
	chName = chName.ljust(32, ' ')
	print("\n","--> Scanning Channel ",chanID)
	cmd = ['/usr/local/bin/aws','--no-paginate','medialive','describe-channel','--channel-id', chanID]
	try:
		CLIReply = GetCLIResult(cmd)
        #print("DecodedReply has heys", CLIReply.keys())
	except:
		print("!! No keys found in CLIReply for cmd: ",cmd)
		print("!! Exiting.")
		exit()

	ThisChanneljson = CLIReply
	
	# Now check the region again
	arnstring=str(ThisChanneljson['Arn'])
	arnlist=arnstring.split(":",9)
	if (myregion != arnlist[3]) :
		myregion = arnlist[3]
		print("-----> Setting region to ",myregion," but you can change it later if needed.")
	
	TotalPipelines = (TotalPipelines + 1)
	counter = 0
	
	for counter in range ( 0, len(WidgetsList) ) :
		try:
			WidgetsList[counter]['properties']['region']= myregion
			QueryString = WidgetsList[counter]['properties']['query']
			ch_old = "CHL=999999"
			ch_new = "CHL="+ str(chanID)
			QueryNew = QueryString.replace(ch_old,ch_new)
			QueryNew = QueryNew.replace("'","%%") ## to preseve single quotes
			QueryNew = QueryNew.replace('"',"@@") ## to preseve double quotes
			WidgetsList[counter]['properties']['query'] = QueryNew
			print("\n\n","BREAK after fixing query","\n\n")
			#code.interact(local=globals())
		except:
			print("unable to add row for widget on Ch ",chanID, "...continuing..." )
			
# ------------------------------------------------------------------------------------
FileOpen = '{"widgets": ['
FileClose = ']}'
## 
WidgetStringsList=[]
#

FullJSON = FileOpen
for counter in range (0, len(WidgetsList)) :
	S = str(WidgetsList[counter])
#	S = S.replace('(','')
#	S = S.replace(')','')
	S = S.replace("'",'"')
	S = S.replace('"false"','false')
	S = S.replace('"true"','true')
	S = S.replace("%%","'")
	S = S.replace('@@',r'\"')
	S+=","
	FullJSON+=S
##
FullJSON = FullJSON[:-1]
FullJSON+=FileClose
##

print("")
dashfile = "./MediaLive_dashjson_" + tstamp + ".json"
f = open(dashfile, 'w')
f.write(FullJSON) 
f.close()
print(tnormal,"\n")

print("----> Dash JSON exported to local file '", dashfile, "' for future reference." )    
##
# ------------------------------------------------------------------------------------

dashname = "Ch"+SingleCh+"_SCTE_Marker_Counts_" + tstamp
dashpath = "file://" + dashfile
print("\n","=================================================================","\n")
print(" Attempting to create new dashboard ",CWHITE, dashname, CEND, "in your CW Console. You can rename the dash via the Console.")
print("...","\n\n")
cmd = ['/usr/local/bin/aws','cloudwatch','put-dashboard','--dashboard-name',dashname,'--dashboard-body', dashpath]
print ("\n\n\n", "trying:", cmd, "\n\n\n")
try:
	CLIReply = GetCLIResult(cmd)
        
except:
	print("!! Dashboard crate command returned error:", CLIReply)
	print("!! Exiting.")
	exit()

print("\n\n"," Cloudwatch upload errors, if any:","\n\n",CWHITE,CLIReply)
print("\n\n",CEND)
print("Remember to set the time range for your new Dashboard (upper right corner of CW Console).","\n\n")

exit()
