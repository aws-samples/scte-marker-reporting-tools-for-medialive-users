# SCTE Reporting Tools for use with AWS Elemental MediaLive

The following tools enable users of AWS ELemental MediaLive to report 
on SCTE markers ingested and processed per hour,  in report or chart form using AWS CLoudWatch logs. 

### Report: Detailed SCTE marker report
CloudWatch Insights query to generate a detailed report of processed SCTE markers from MediaLive logs.
Includes Avail IDs, Pre-roll times, splice types, output details and more. 

Find the report [query here](https://raw.githubusercontent.com/aws-samples/scte-marker-reporting-tools-for-medialive-users/main/SCTE%20Marker%20detailed%20report%20query.txt?token=GHSAT0AAAAAACNDCHFHQZKUVSNC7QVIGLFEZN26BPA). Just copy & paste into your CloudWatch console.


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

You can quickly create a new CloudWatch dashboard with a Marker counts widget using this one-liner in your AWS CLI or CLoudShell prompt:
**python3 -c "$(curl -fsSL https://raw.githubusercontent.com/aws-samples/scte-marker-reporting-tools-for-medialive-users/main/create_Scte_Marker_counts.py)"**


Or download the script [here](https://raw.githubusercontent.com/aws-samples/scte-marker-reporting-tools-for-medialive-users/main/create_Scte_Marker_counts.py?token=GHSAT0AAAAAACNDCHFHODHZBA7MR5DGSSUGZN26CIA)

Example JSON for this chart with embedded query [here](https://github.com/aws-samples/scte-marker-reporting-tools-for-medialive-users/blob/main/example%20widget%20chart%20code.json)

For a tabular report of Marker counts, use CloudWatch query [here](https://raw.githubusercontent.com/aws-samples/scte-marker-reporting-tools-for-medialive-users/main/example_query_marker_counts_per_hour?token=GHSAT0AAAAAACNDCHFH4MXORNUPITTTSF74ZN253PQ)
