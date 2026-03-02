# cl-api-doc Notebook Index

Source: `/Users/j8ck/.codex/skills/corticallabs-api/references/external/cl-api-doc`

## CL-00. Hello, Neurons.ipynb
- Notebook focus: # Hello, Neurons.  Say hello to some neurons with a small amount of electrical stimulation! Keep the visualiser visible, and run this cell to stimulate a **channel** with one microampere of electrical current in each pol
- Additional note: Each time you run this code, you'll see stimulation activity in a channel near the centre of the visualiser. You may also notice a change in the behaviour of nearby neurons.
- Example code 1: `import cl  with cl.open() as neurons:     # Stimulate channel 27 with 180µs of -1.5µA, then 180µs of +1.5µA.     neurons.stim(         cl.ChannelSet(27),         cl.StimDesign(180, -1.5, 180, 1.5))`
- Example code 2: `import cl  with cl.open() as neurons:     # Stimulate multiple channels with 180µs of -1.5µA, then 180µs of +1.5µA.     neurons.stim(         cl.ChannelSet(27, 28, 35, 36),         cl.StimDesign(180, -1.5, 180, 1.5))`

## CL-01. Detecting and Reacting to Spikes.ipynb
- Notebook focus: # Detecting and Reacting to Spikes  The Loop API allows you easily and quickly react to action potentials (spikes).  This toy example loops 1000 times per second for 5 seconds, and stimulates any electrode where a spike 
- Additional note: Each iteration makes detected action potentials and other data available via the tick object. This makes it easy to embody your lab-grown brain cells within a closed loop simulation:
- Example code 1: `import cl  with cl.open() as neurons:     for tick in neurons.loop(ticks_per_second=1000, stop_after_seconds=5):         for spike in tick.analysis.spikes:             neurons.stim(spike.channel, 1)`
- Example code 2: `import cl  with cl.open() as neurons:          # TODO: Initialise a simulated environment      # Now run the closed loop     for tick in neurons.loop(ticks_per_second=100):           # TODO: Use tick.analysis.spikes to u`

## CL-01A. Detecting and Reacting to Spikes. Appendix A. UDP Spike Receiver.ipynb
- Example code 1: `# # CL-01A. Detecting and Reacting to Spikes. Appendix A. UDP Spike Receiver # # This example program waits for and displays UDP packets of spike # information sent by an example in CL-01. # # We will likely add first-cl`

## CL-02. Recording.ipynb
- Notebook focus: # Recording  A recording subsystem is provided to record live data into a HDF5 file, leaving your code free to focus on the experiment.  This example demonstrates making a recording while performing an arbitrary task:
- Additional note: The above is great for performing arbitrary length recordings. However, if you specifically wanted a 3 second recording, you'd ask the system to automatically stop the recording after 3 seconds:
- Example code 1: `import cl import time  with cl.open() as neurons:     recording = neurons.record()          # Recording has started. Here we use sleep to simulate an     # arbitrary blocking foreground task (such as a game loop!)     # `
- Example code 2: `import cl  with cl.open() as neurons:     recording = neurons.record(stop_after_seconds=3)     recording.wait_until_stopped()      attrs = recording.attributes print(f"Recorded {attrs['duration_frames']} frames ({attrs['`

## CL-03. Data Streams.ipynb
- Notebook focus: # Data Streams  Data streams allow client applications to publish named streams of arbitrary structured data which are added to recordings and are available for live visualisation.  Each entry in a single data stream is 
- Additional note: ## DataStreamView  The HD5F format does not natively provide for an inituitive way to efficiently store an indexed list of items where any item can be a different size. For this reason, data stream data is stored end-to-
- Example code 1: `import cl import numpy  with cl.open() as neurons:     # Create a named data stream - by default, it will be added to any active or future recordings.     data_stream = \         neurons.create_data_stream(             n`
- Example code 2: `data_stream = recording_view.data_streams.example_data_stream  print(f"There are {len(data_stream)} entries in example_data_stream.")`

## CL-04. Real-Time Visualisation.ipynb
- Notebook focus: ## Real-Time Visualisation  Jupyter data stream visualisation widgets can be created with a HTML snippet and the implementation of a few JavaScript functions. A python API python method is provided to inject these into t
- Additional note: This example subscribes to a custom 'gameplay' data stream, displays a canvas for drawing on, and adds a html table for attributes.  Lets create a simple moving ball simulation that publishes data to the 'gameplay' data 
- Example code 1: `from cl.visualisation.jupyter import display_visualiser  display_visualiser(     html_file='assets/CL-04. Example Visualiser.html',     javascript_file='assets/CL-04. Example Visualiser.mjs',     data_streams=['gameplay'`
- Example code 2: `import cl import random import math  DURATION_SECONDS   = 30 HZ                 = 100 TICK_DELTA_SECONDS = 1 / HZ  GAME_WIDTH         = 320 GAME_HEIGHT        = 180 BALL_WIDTH         = 10 BALL_HEIGHT        = 10  BALL_S`

## CL-05. Reading Raw Data.ipynb
- Notebook focus: # Reading Raw Data  ## Samples, Frames, and Timestamps  A **sample** is a 16-bit signed measurement from a single electrode. A **frame** contains a single sample from each of the 64 electrodes. The system runs at a fixed
- Additional note: ## Reading Live Data  An API is provided to read an arbitrary number of frames of raw samples from a recent or future timestamp. For example, to read a single frame from the current timestamp:
- Example code 1: `import cl import time  with cl.open() as neurons:     first_timestamp = neurons.timestamp()          # Wait for (at least) 1 second     time.sleep(1)          second_timestamp = neurons.timestamp()      print(f"The first`
- Example code 2: `import cl  with cl.open() as neurons:     frame = neurons.read(1, neurons.timestamp())  print(frame)`

## CL-06. Stimulation.ipynb
- Notebook focus: # Stimulation.  Complex stimulation requires moving beyond the simple stimulation methods available in the neurons object.  TBA :)
