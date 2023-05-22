# astropix-python-v3

Example - Run Scripts
---------------------
  - Digital Noise Scan pixel by pixel
```bash
python3.9 noise_scan.py -n "filename" -o./outputdirectory -c -M 0.084 -t 400.0 -C 0 34 -R 0 34
```

  - Pixel Scan with Injection
```bash
python3.9 pixelScan_injection.py -n "filename" -C 0 0 -R 0 0 -v 300.0 -t 400.0
```

  - Beam Measurement with Masking
```bash
python3.9 beam_test.py -n "filename" -o ./outputdirectory -ns ./noise_scan.csv -c -t 200.0 -L W
```

  - Pixel Hit Plot per Run (Beam measurement)
```bash
python3.10 generate_event_display.py -d "./datadirectory" -o "./outputdirectory" -l 1
```

## How to run beam measurement scripts at TestBeam

### Step 0 Pre-Run
The computer for Astropix DAQ control and data analysis is located on the right from the entrnance to the control room (MTEST facility) with 4 monitors. The machine is called dhcp-131-225-179-117. 

The computer to run the MWPC scripts is ftbf-cr-05 (opposite to the one above) where the FTBF Faciliy status is displayed.  

### Step 1 Find LogBook
Find beam measurement logbook (in a format xlsx) through Argonne Box. (https://anl.box.com/s/41tpng6pd600mgh9r7cuqiqs1z43i52n)
Other materials including beam profiles and noise scans can be found in (https://anl.app.box.com/folder/192431367188)

### Step 2 Log in the AstroPix Computer
On dhcp-131-225-179-117 there should be already terminal with established connection to the AstroPix DAQ computer inside the enclosure. If not follow the instruction below.

Log into a computer in enclosure remotely by
```
ssh labadmin@mtestfedorapc.dhcp.fnal.gov
```
All scripts are stored in a directory
```
cd /home/labadmin/AstropPix/astropix-python
```

### Step 3 Run Beam Measurement
When the beam is requested, tunned, and stable start the experimental run. 

Use the following script. Remeber to change the run number, and note in the logbook all the required parameters. Please make note of any changing circumstances, parameters, basically anything. Better note down something than not.  

Run beam measurement script
```
python3.9 beam_test.py -o "/home/labadmin/AstropPix/BeamTest2023/BeamData/Chip_230103" -y testconfig -ns "/home/labadmin/AstropPix/BeamTest2023/NoiseScan/Chip_230103/noise_scan_summary_chip230208_20230220-012049.csv" -t 600.0 -L W -nt 5 -M 60 --ludicrousspeed -n "run22_proton120GeV"
```
- option `-o`: directory where output data file is stored
- option `-y`: configuration file of astropix chip
- option `-ns`: input noise scan summary file to mask noisy pixels
- option `-t`: threshold voltage for digital ToT (in mV)
- option `-L`: log level WARNING
- option `-M`: maximum run time (in minutes)
- **option `-n`: name of data output file** (REMEMBER TO CHANGE)

### Step 4 Record Beam Profile
Take screenshot of beamprofile from GxSA: Meson Line Profiles v8.24 by `Alt + Print Screen`. All screenshots are stored in `/home/nfs/ftbf_user/Pictures/`. You can find an example here (https://anl.box.com/s/yqkeppf8jyh6c9fr3ia7yomvr3o72812)

At the begining of each run, please record the data from MWPC on the ftbf-cr-05. After run finishes, make the plots of the profile and put them to the Box in the directory measurements/BeamProfile. Refer to the instructions how to run the beam scan in https://anl.box.com/s/it15ejcoxm2hil1for09byczogue599e (also displayed on the dhcp computer)


### Step 5 Run Decode Data (Post-Run)
Run decode script (offline) after data-taken
```
python3.9 decode_postRun.py -f "/home/labadmin/AstropPix/BeamTest2023/BeamData/Chip_230103/run22_*.log" -o "/home/labadmin/AstropPix/BeamTest2023/BeamData/Chip_230103" -L D -p
```
- **option `-f`: input data file to decode** (REMEMBER TO CHANGE) 
- option `-o`: directory where decoded output data file is stored
- option `-L`: log level DEBUG
- option `-p`: Print decoded info into terminal

### Step 6 Make Figure (Post-Run)
Run plotting script script
```
python3.9 generate_event_display.py -n "proton_120GeV_chip230103" -o "/home/labadmin/AstropPix/BeamTest2023/Plots" -d "/home/labadmin/AstropPix/BeamTest2023/BeamData/Chip_230103" -l 22
```
- option `-n`: name of histogram and output file
- option `-o`: directory where output plot file is created
- option `-d`: directory where decoded beam data is located
- **option `-l`: run numbers of data that we would like to see**   ex) `-l 22` run22 only or `-l 20 21 22` run 20, 21, and 22 data combined

scp .png plots to the dhcp computer in the control room. Add plots to the Box under measurements/RunPlots. You can also send the to Slack. 

