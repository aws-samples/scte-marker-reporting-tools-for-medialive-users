# SCTE Reporting Tools for use with AWS Elemental MediaLive

The following tools enable MediaLive users to use AWS CloudWatch to report 
on SCTE markers ingested and processed per hour,  in report or chart form.

### Report: Detailed SCTE marker report
CloudWatch Insights query to generate a detailed report of processed SCTE markers from MediaLive logs.
Includes Avail IDs, Pre-roll times, splice types, output details and more. 

Find the report [query here](https://github.com/aws-samples/scte-marker-reporting-tools-for-medialive-users/blob/main/SCTE%20Marker%20detailed%20report%20query). Just copy & paste into your CloudWatch console:

![](https://github.com/aws-samples/scte-marker-reporting-tools-for-medialive-users/blob/main/example_query_report.jpg?raw=true)
- - - - - -

### Chart: SCTE Marker Counts chart
Code and script to generate a CloudWatch dashboard which charts counts of SCTE markers ingested and output.

Notes:  
- use 'IngestM2TS' for markers/cues ingested
- use 'OutputContentM2TS'  for for Markers embedded into  mpeg2 transport stream output carried via bitstream formats (RTP, RTMP etc)
- use 'OutputPlaylistHLS' for CUEs & markers added to output HLS manifests as Tags
- use 'OutputContentHLS' for Markers embedded into transport steam segments
- time signals are often used to schedule markers at some future time, accounting for a gap between ingest time and output time
- auto-return may account for various 'end of break' markers without any corresponding 'CUE-IN' ingested. 
- all MediaLive log syntax is mutable and subject to change as improvements are introduced. You may have to update your queries in future. 
  
![](https://github.com/aws-samples/scte-marker-reporting-tools-for-medialive-users/blob/main/example-Marker-Counts-chart.jpg?raw=true)

Find the example JSON for this chart [here](https://github.com/aws-samples/scte-marker-reporting-tools-for-medialive-users/blob/main/example%20widget%20chart%20code.json)
