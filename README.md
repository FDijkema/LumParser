# About LumParser
What is LumParser?
- a Python library
- a standalone programme where you can interact with luminescence data through a user interface

If you perform bioluminescent enzymatic reactions and record the light output over time in a spectrometer, you can use
LumParser to analyze the resulting data. It saves you the hassle of copy-pasting the data in Excel and subtracting the
light background by hand. Plus, you get more options for fitting of data than in Excel.

The program was built to take ascii time drive files as input and detecting features of a typical run:
- An initial phase of around 10s to record the background light, with a luciferase in the reaction mixture.
- Injection of substrate (luciferin) around 10s into the recording, starting light emission. The entire period in which
light is emitted is referred to as a signal and the initial spike in light as a peak.
- Slow decay of the light signal over a period of time, which can be fitted to an exponential decay curve.

A run can contain several signals if multiple substrate injections are performed, so multiple signals can be detected by
the program.


# Requirements

  * Python 3.7
  * Python third-party packages:
    * matplotlib
    * numpy
    * scipy

# Input files
Input time drive files are text files with the extension ".td". The files can contain a header with information. After
the header, a line reading

```
#DATA
```
should precede the section of the file containing the recorded datapoints.
Data should be in time/value pairs, separated by whitespace. The expected units are seconds (s) for time and relative light
units (RLU) for light emission.

# Signal detection
The following rules are used to detect a signal:
- The start of the signal cannot overlap with the background. So, if the background is measured between 0 and 10s, a
signal start at 9.5s will not be detected.
- The light emission value should increase by more than the threshold value compared to the average of the last 10
datapoints. So, if the threshold is set to 0.3 and the average of the last 10 datapoints is 5.0, the next datapoint
should have a value of 5.3 or higher for a signal to be detected. The average of the last 10 datapoints before the start
is taken as the baseline.
- If the light emission dips below baseline withing 100 datapoints after the initial increase, the increase is assumed 
to be the result of noise instead of a signal.
- To make sure that it is always possible to check the rule above, no signal starts can be recorded in the last 100
datapoints in a file.
- A signal ends at the start of the new signal or at the end of the file.
- When a signal is recorded and parsed, the background light value is subtracted from all datapoints and the starting
time is set to 0s.

# Installing
To be written...

# Using the interface

Run the interface from command line using:

```
python LumParser
```

The interface will open and ...
