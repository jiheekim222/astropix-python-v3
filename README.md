# astropix-python

Python based lightweight cross-platform tool to control the GECCO System, based on [ATLASPix3_SoftAndFirmware](https://git.scc.kit.edu/jl1038/atlaspix3)

To interact with the FTDI-Chip the ftd2xx package is used, which provides a wrapper around the proprietary D2XX driver.
The free pyftdi driver currently does not support the synchronous 245 FIFO mode.  
For bit manipulation the bitstring package is used.

Features:
* Write ASIC config (SR and SPI)
* Configure Voltageboards (+offset cal)
* Configure Injectionboard
* Read/Write single registers
* SPI/QSPI Readout
* Import/export chip config from/to yaml

Work in progress:
* GUI
* Scans

## Installation

Requirements:
* Python >= 3.9
* packages: ftd2xx, async-timeout, bitstring 
* D2XX Driver

```shell
$ git clone git@github.com:nic-str/astropix-python.git
$ cd astropix-python

# Create venv
$ python3 -m venv astropix-venv
$ source astropix-venv/bin/activate

# Install Requirements
$ pip install -r requirements.txt
```

### Windows

D2XX Driver should be pre-installed.

### Linux

Install D2XX driver: [Installation Guide](https://ftdichip.com/wp-content/uploads/2020/08/AN_220_FTDI_Drivers_Installation_Guide_for_Linux-1.pdf)

Check if VCP driver gets loaded:
    
    sudo lsmod | grep -a "ftdi_sio"

If yes, create a rule e.g., 99-ftdi-nexys.rules in /etc/udev/rules.d/ with the following content to unbid the VCP driver and make the device accessible for non-root users:

    ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6010",\
    PROGRAM="/bin/sh -c '\
        echo -n $id:1.0 > /sys/bus/usb/drivers/ftdi_sio/unbind;\
        echo -n $id:1.1 > /sys/bus/usb/drivers/ftdi_sio/unbind\
    '"

    ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6010",\
    MODE="0666"

Reload rules with:

    sudo udevadm trigger

Create links to shared lib:

    sudo ldconfig

### Mac
See [FTDI Mac OS X Installation Guide](https://www.ftdichip.com/Support/Documents/InstallGuides/Mac_OS_X_Installation_Guide.pdf) D2XX Driver section from page 10.

# How to use the astropix2 module
Astropix-py is a module with the goal of simplifying and unifying all of the diffrent branches and modulles into a single module which can be easily worked with. 
The goal is to provide a simple interface where astropix can be configured, initalized, monitored, and iterfaced with without having to modify source files or copy and paste code from various repositories. 

Although we aim to maintain compatibility with older branches, that will not be possible in all cases (for example the asic.py module). When this happens the original files will be preserved to maintain backwards compatibility and directions and information for moving over to the new interface.

## Directions for use:
Must go in this order!!

1. Creating the instance
    - After import, call astropix2().
    - Usage: `astropix2([none required], clock_period_ns: int, inject: bool)`
    - optional arguments: 
        - clock_period_ns, default 10
        - inject, default `False`. When true configures the pixels to accept an injection voltage
2. Initializing voltages
    - call `astro.init_voltages([none required] slot, vcal, vsupply, vthreshold, [optional] dacvals)`
    - slot: Usually 4, tells chip where the board is
    - vcal: calibrated voltage. Usually 0.989
    - vsupply: voltage to gecco board, usually 2.7
    - vthreshold: ToT threshold voltage. Usually 1.075 ish    
    - optional, dacvals: if you want to configure the dac values, do that here
3. Initalizing the ASIC
    - call `astro.asic_init()`
    - Usage: `astro.asic_init(yaml:str, [opt] dac_setup: dict, bias_setup: dict, digital_mask: str)`
    - Optional arguments:
        - yaml: string of name of configuration .yml file in /config/*.yml. If none given command-line, default set to config/testconfig.yml
        - dac_setup: dictionary of values which will be used to change the defalt dac settings. Does not need to have a complete dictionary, only values that you want to change. Default None
        - bias_setup: dictionary of values which will be used to change the defalt bias settings. Does not need to have a complete dictionary, only values that you want to change. Default None
        - digital_mask: text data of 1s and 0s in a 35x35 grid (newline seperated rows) specifying what pixels are on and off. If not specified chip will be in analog mode
4. Initalizing injector board (optional)
    - call `astro.init_injection()`
    - Has following options and defaults:
        - dac_settings:tuple[int, list[float]] = (2, [0.4, 0.0])
        - position: int = 3, position in board, same as slot in init_voltages().
        - inj_period:int = 100 
        - clkdiv:int = 400
        - initdelay: int = 10000 
        - cycle: float = 0
        - pulseperset: int = 1
5. enable SPI
    - `astro.enable_spi()`
    - takes no arguments

Useful methods:

astro.hits_present() --> bool. Are thre any hits on the board currently?

astro.get_readout() --> bytearray. Gets bytestream from the chip

astro.decode_readout(readout, [opt] printer) --> list of dictionaries. Printer prints the decoded values to terminal

astro.write_conf_to_yaml(<outputName>) --> write configuration settings to *.yml

astro.start_injection() and astro.stop_injection() are self explainatory

## Usage of beam_test.py

beam_test.py is a rewritten version of beam_test.py which removes the need for asic.py, and moves most configuration to command arguments.
It has the ability to:
- Save csv files
- Plot hits in real time
- Configure threshold and injection voltages 
- Enable digital output based on pixel masks 

CAUTION : try not to pass arguments to astropix.py as numpy objects - if looping through a numpy array, typecast to int, float, etc for the argument call or features may not work as intended (ie - pixels may not be activated/deactivated as expected)

Options:
| Argument | Usage | Purpose | Default |
| :--- | :--- | :---  | :--- |
| `-n` `--name` | `-n [SOMESTRING]` | Set additional name to be added to the timestamp in file outputs | None |
| `-o` `--outdir`| `-o [DIRECTORY]` | Directory to save all output files to. Will be created if it doesn't exist. | `./` |
| `-y` `--yaml`| `-y [NAME]` | Name of configuration file, assuming config/*.yml where * is passed. If not specified, uses config/testconfig.yml and disables all pixels | `testconfig` |
| `-c` `--saveascsv` | `-c`         | Toggle saving csv files on and off | Does not save csv |
| `-s` `--showhits` | `-s`          | Display hits in real time | Off |
| `-p` `--plotsave` | `-p`          | Saves real time plots as image files. Stored in outdir. | Does not save plots |
| `-t` `--threshold`| `-t [VOLTAGE]`| Sets digital threshold voltage in mV. | `100mV` |
| `-i` `--inject`| `-i [COL]`       | Toggles injection on or off at specified column. Injects 300mV unless specified. | Off|
| `-v` `--vinj` | `-v [VOLTAGE]`    | Sets voltage of injection in mV. Does not enable injection. | `300mV` |
| `-M` `--maxruns` | `-M [int]`     | Sets the maximum number of readouts the code will process before exiting. | No maximum |
| `-E` `--errormax`| `-E [int]`     | Amount of index errors encountered in the decode before the program terminates. | `0` |
| `-a` `--analog` | `-a [COL]`      | Enable analog output on specified column | `None` |
| `-L` `--loglevel` | `-L [D,I,E,W,C]`| Loglevel to be stored. Applies to both console and file. Options: D - debug, I - info, E - error, W - warning, C - critical | `I` |
| `--timeit` | `--timeit`           | Measures the time it took to decode and store a hitstream. | Off |


Example - Run Scripts
---------------------
  - Digital Noise Scan pixel by pixel
```bash
python3.9 noise_scan.py -n "filename" -o./outputdirectory -c -M 0.084 -C 0 34 -R 0 34
```

  - Pixel Scan with Injection
```bash
python3.9 pixelScan_injection.py -n "filename" -C 0 0 -R 0 0 -v 300.0
```

  - Beam Measurement with Masking
```bash
python3.9 beam_test.py -n "filename" -o ./outputdirectory -y testconfig -ns ./noise_scan.csv -c -t 200.0 -L W
```

  - Pixel Hit Plot per Run (Beam measurement)
```bash
python3.10 plot_hits.py -df "./beam_measurement.csv" -o "./outputdirectory" -rn 1 -n "protons120"
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
```
At the begining of each run, please record the data from MWPC on the ftbf-cr-05. After run finishes, make the plots of the profile and put them to the Box in the directory measurements/BeamProfile. Refer to the instructions how to run the beam scan in https://anl.box.com/s/it15ejcoxm2hil1for09byczogue599e (also displayed on the dhcp computer)
```

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
python3.9 plot_hits.py -n "proton_120GeV_chip230103" -o "/home/labadmin/AstropPix/BeamTest2023/Plots" -d "/home/labadmin/AstropPix/BeamTest2023/BeamData/Chip_230103" -l 22
```
- option `-n`: name of histogram and output file
- option `-o`: directory where output plot file is created
- option `-d`: directory where decoded beam data is located
- **option `-l`: run numbers of data that we would like to see**   ex) `-l 22` run22 only or `-l 20 21 22` run 20, 21, and 22 data combined

scp .png plots to the dhcp computer in the control room. Add plots to the Box under measurements/RunPlots. You can also send the to Slack. 

