# cl-sdk Public Signatures

Source root: `/Users/j8ck/.codex/skills/corticallabs-api/references/external/cl-sdk`

## src/cl/__init__.py

- `class Stim`
  - A Stim object is created for each stim delivered by the system.
- `class Spike`
  - A Spike object is created for each spike detected by the system.
- `class DetectionResult`
  - A DetectionResult that holds spikes and stims at a given timestamp.
  - `def timestamp(self) -> int`
    - Timestamp of the first processed frame in this result.
- `class ChannelSet`
  - Stores a set of channels for stimulation.
- `class StimDesign`
  - Stores the parameters of a mono, bi, or triphasic stim design by specifying
- `class BurstDesign`
  - Stores the parameters of a stimulation burst.
- `def open(take_control: bool = True, wait_until_recordable: bool = True) -> Generator[Neurons]`
  - Open a connection to the device, optionally take and retain control,
- `def get_system_attributes() -> dict[str, Any]`
  - Gets the system attributes that are included in each recording as a dictionary.

## src/cl/neurons.py

- `class Neurons`
  - The `Neurons` class provides the main interface with the CL1 hardware. This should
  - `def stim(self, channel_set: ChannelSet | int, stim_design: StimDesign | float, /, burst_design: BurstDesign | None = None, lead_time_us: int = 80) -> None`
    - Stimulate one or more channels.
  - `def interrupt(self, channel_set: ChannelSet | int, /) -> None`
    - Interrupt existing and clear any pending stimulation for the specified channels.
  - `def interrupt_then_stim(self, channel_set: ChannelSet | int, stim_design: StimDesign | float, /, burst_design: BurstDesign | None = None, lead_time_us: int = 80) -> None`
    - Interrupt existing and cancel queued stimulation, then send a stim burst. This is equivalent to
  - `def sync(self, channel_set: ChannelSet, /, wait_for_frame_start: bool = True) -> None`
    - Prevent further queued stimulation until all channels have reached this sync point.
  - `def create_stim_plan(self) -> StimPlan`
    - Create a new `StimPlan` object to build a stimcode plan.
  - `def loop(self, ticks_per_second: float, stop_after_seconds: float | None = None, stop_after_ticks: int | None = None, ignore_jitter: bool = False, jitter_tolerance_frames: int = 0) -> Loop`
    - Periodically detect spikes and execute code. (Relates to `Loop` and `LoopTick`.)
  - `def record(self, file_suffix: str | None = None, file_location: str | None = None, from_seconds_ago: float | None = None, from_frames_ago: int | None = None, from_timestamp: int | None = None, stop_after_seconds: float | None = None, stop_after_frames: int | None = None, attributes: dict[str, Any] | None = None, include_spikes: bool = True, include_stims: bool = True, include_raw_samples: bool = True, include_data_streams: bool = True, exclude_data_streams: list[str] = []) -> Recording`
    - Start a new HDF5 recording.
  - `def create_data_stream(self, name: str, attributes: dict[str, Any] | None = None) -> DataStream`
    - Publish a named stream of (timesamp, serialised_data) for recordings and visualisation.
  - `def get_channel_count(self) -> int`
    - Get the number of channels (electrodes) the device supports.
  - `def get_frames_per_second(self) -> int`
    - Get the number of frames per second the device is configured to produce.
  - `def get_frame_duration_us(self) -> float`
    - Get the duration of a frame in microseconds.
  - `def timestamp(self) -> int`
    - Get the current timestamp of the device.
  - `def read(self, frame_count: int, from_timestamp: int | None = None, /) -> ndarray[tuple[int, int], np.dtype[np.int16]]`
    - Read `frame_count` frames from the neurons, starting at `from_timestamp`
  - `def read_async(self, frame_count: int, from_timestamp: int | None = None) -> ndarray[tuple[int, int], np.dtype[np.int16]]`
    - Asynchronous version of read().
  - `def has_control(self) -> bool`
    - Indicates whether control has been obtained.
  - `def take_control(self) -> None`
    - Take control of the device. Only one process can take control at a time.
  - `def release_control(self) -> None`
    - Release control of the device.
  - `def is_readable(self) -> bool`
    - Returns `True` if the device can be read from.
  - `def wait_until_readable(self, timeout_seconds: float = 15)`
    - Blocks until the device can be read from, raising a `TimeoutError` if the
  - `def is_recordable(self) -> bool`
    - Return `True` if the device is recordable.
  - `def wait_until_recordable(self, timeout_seconds: float = 15)`
    - Blocks until the recording system is ready, raising a `TimeoutError` if
  - `def start(self) -> None`
    - Start the device if has not already started.
  - `def has_started(self) -> bool`
    - Returns `True` if the device has started.
  - `def restart(self, timeout_seconds: int = 15, wait_until_recordable: int = True) -> None`
    - Restart the device and wait until it is readable, and optionally, recordable.
  - `def stop(self) -> None`
    - Stop the device if it has started.
  - `def close(self) -> None`
    - Closes the connection to the CL1. If we have control, ensure stimulation is off,

## src/cl/recording.py

- `class Recording`
  - Handles recording functionality by the CL1 system. This is returned when
  - `def open(self)`
    - Return a `RecordingView` of the recoding file.
  - `def set_attribute(self, key: str, value: Any)`
    - Set a single application attribute on the recording. The application attribute
  - `def update_attributes(self, attributes: dict[str, Any])`
    - Update multiple application attributes on the recording. The application attribute
  - `def stop(self)`
    - Stop the recording, if not already stopped.
  - `def has_stopped(self)`
    - Return `True` if the recording has stopped.
  - `def wait_until_stopped(self)`
    - Wait until the recording has stopped.

## src/cl/data_stream.py

- `class DataStream`
  - Manages a named stream of (timestamp, serialised_data) for recordings and visualisation.
  - `def append(self, timestamp: int, data: Any)`
    - Append a new data point to the stream.
  - `def set_attribute(self, key: str, value: Any)`
    - Set a single attribute on the data stream. The attribute refers to the
  - `def update_attributes(self, attributes: dict[str, Any])`
    - Update multiple attributes on the data stream. The attribute refers to the

## src/cl/_stim_plan.py

- `class Operation`
- `class StimPlan`
  - Allows building and executing a sequence of stim operations that can be run on demand. The `StimPlan`
  - `def stim(self, channel_set: ChannelSet | int, stim_design: StimDesign | float, /, burst_design: BurstDesign | None = None, lead_time_us: int = 80) -> None`
    - Enqueues the same operation as `Neurons.stim()` onto this `StimPlan`.
  - `def interrupt(self, channel_set: ChannelSet | int, /) -> None`
    - Enqueues the same operation as `Neurons.interrupt()` onto this `StimPlan`.
  - `def interrupt_then_stim(self, channel_set: ChannelSet | int, stim_design: StimDesign | float, /, burst_design: BurstDesign | None = None, lead_time_us: int = 80) -> None`
    - Enqueues the same operation as `Neurons.interrupt_then_stim()` onto this `StimPlan`. This is equivalent to
  - `def sync(self, channel_set: ChannelSet, /) -> None`
    - Enqueues the same operation as `Neurons.sync()` onto this `StimPlan`.
  - `def channels_to_interrupt(self) -> ChannelSet | None`
    - Allows specification of channels to interrupt when this plan is run.
  - `def channels_to_interrupt(self, channel_set: ChannelSet | int | None, /)`
    - Setter for channels_to_interrupt.
  - `def run(self, at_timestamp: int | None = None) -> None`
    - Execute the queued operations in the `StimPlan`. After this method is called,

## src/cl/util/recording_view.py

- `class RecordingView`
  - Recording files are standard HDF5 files and can be opened with any
  - `def close(self)`
    - Close the underlying PyTables file.
  - `def analyse_firing_stats(self, bin_size_sec: float = 1.0) -> AnalysisResultFiringStats`
    - Compute firing statistics efficiently for a neural recording by binning spike activity into fixed-width time bins..
  - `def analyse_network_bursts(self, bin_size_sec: float, onset_freq_hz: float, offset_freq_hz: float, min_active_channels: int | None = None) -> AnalysisResultNetworkBursts`
    - Detects network-level bursts from spike data using a spike rate thresholding method.
  - `def analyse_criticality(self, bin_size_sec: float, percentile_threshold: float, max_lags_branching_ratio: int = 40, duration_thresholds: tuple[int, int] = (2, 5), min_spike_count_threshold: int = 10, n_bootstraps: int = 100, random_seed: int = 42) -> AnalysisResultCriticality`
    - Detects **neuronal avalanches** and computes criticality-related metrics such as avalanche size distributions,
  - `def analyse_information_entropy(self, bin_size_sec: float, fillna: float | None = 0.0, log_base: float | None = None) -> AnalysisResultInformationEntropy`
    - Computes per-bin Bernoulli entropy of the fraction of channels that have >=1 spike in the bin.
  - `def analyse_lempel_ziv_complexity(self, bin_size_sec: float, min_bin_count: int = 2, normalise: bool = True, use_binary: bool = True) -> AnalysisResultComplexityLempelZiv`
    - Computes **Lempel–Ziv complexity (LZ78)** for each channel’s binned spike activity, measuring temporal complexity
  - `def analyse_dct_features(self, k: int) -> AnalysisResultDctFeatures`
    - Calculates the Discrete Cosine Transform (DCT) features based on channel spike counts.
  - `def analyse_spike_triggered_histogram(self, bin_size_sec: float, start_sec: float, end_sec: float, num_channels: int, min_firing_rate_threshold_hz: float = 0.1) -> AnalysisResultSpikeTriggeredHistogram`
    - Generates spike-triggered histograms using the most active channels as triggers,
  - `def analyse_functional_connectivity(self, bin_size_sec: float, correlation_threshold: float = 0.6) -> AnalysisResultsFunctionalConnectivity`
    - Compute functional connectivity (based on Pearson correlation) and
  - `def plot_spike(spike: tuple[int, int, np.ndarray[tuple[int], np.dtype[np.float64]]] | Spike, figsize: tuple[int, int] = (6, 2), title: str | None = None, save_path: str | None = None, ax: Axes | None = None)`
    - Creates a plot of a single spike.
  - `def plot_spikes_and_stims(self, figsize: tuple[int, int] = (12, 8), title: str | None = None, save_path: str | None = None, limit_to_time_range_secs: tuple[float, float] | None = None, limit_to_channels: list[int] | None = None)`
    - Creates a raster plot of spikes and stims in the recording.
- `class AttributesView`
  - `def keys(self)`
  - `def items(self)`
  - `def values(self)`
- `class AttributesDict`
  - Describes attributes that is typically contained within a recording and can be
- `class DataStreamCollection`
  - Interface for accessing a collection of DataStreams.
  - `def keys(self) -> Generator[str, None, None]`
  - `def items(self) -> Generator[tuple[str, DataStreamView], None, None]`
  - `def values(self) -> Generator[DataStreamView, None, None]`
- `class DataStreamView`
  - Provides a read-only interface to data stream entries.
  - `def data_for_entry(data, entry: Group)`
  - `def keys(self) -> DataStreamKeysView`
  - `def values(self) -> DataStreamValuesView`
  - `def items(self) -> DataStreamItemsView`
  - `def keys_for_range(self, start_timestamp, end_timestamp)`
    - Get all keys (timestamps) from start_timestamp up to but not including end_timestamp.
  - `def values_for_range(self, start_timestamp, end_timestamp)`
    - Get all values from start_timestamp up to but not including end_timestamp.
  - `def items_for_range(self, start_timestamp, end_timestamp)`
    - Get all items from start_timestamp up to but not including end_timestamp.

## src/cl/app/base.py

- `class BaseApplicationConfig`
  - Base class for application configurations to inherit from.
  - `def estimate_duration_s(self) -> float | None`
    - Optionally override this method to provide an estimate of the duration (in seconds) of a run through of the application
- `class OutputType`
  - Types of output generated by an application run summary.
- `class RunSummary`
  - Dictionary-based run summary supporting arbitrary fields.
  - `def type(self) -> OutputType`
    - The output type of this summary.
- `class BaseApplication`
  - Base class for applications that can be run on the device.
  - `def run(self, config: T, output_directory: str) -> RunSummary | None`
    - Run the application with the given configuration, saving results and raw outputs to the specified relative path within the
  - `def config_class() -> type[T]`
    - Return the configuration class used by this application.

## src/cl/app/model/model.py

- `class FrozenBaseModel`
  - A Pydantic BaseModel with frozen (immutable) instances, and extra fields forbidden.
- `class StimPulseComponentModel`
  - A single component of a stimulation pulse, either a negative or positive leading-edge phase.
  - `def validate_non_zero_amplitude(cls, value: float) -> float`
    - @private
- `class StimDesignModel`
  - Configuration for a single stimulation design.
  - `def validate_pulse_signs(cls, value: list[StimPulseComponentModel]) -> list[StimPulseComponentModel]`
    - @private
  - `def to_stim_design(self) -> StimDesign`
    - Converts the stimulation design configuration model to a `StimDesign` instance that can be used directly for stimulation.
- `class StimFrequencyRangeHzModel`
  - A valid stimulation frequency range in Hz.
  - `def span(self) -> StimFrequencyHz`
    - Returns the span of the range, i.e. the difference between max and min.
  - `def validate_max(cls, value: StimFrequencyHz, info: ValidationInfo) -> StimFrequencyHz`
    - @private
- `class SizeIntModel`
  - Base class for positive 2D integer size configurations.

## src/cl/analysis/__init__.py


## src/cl/visualisation/visualisation.py

- `def create_iframe_visualiser(iframe_url: str, use_sidebar: bool = True, aspect_ratio: float | None = None) -> str`
  - Create the HTML needed to display an iframe in a Jupyter notebook.
- `def create_visualiser(javascript_file: str | Path, html_file: str | Path | None = None, data_streams: list[str] | None = None, use_sidebar: bool = True, aspect_ratio: float | None = None) -> str`
  - Create the HTML needed to display a custom visualiser in a Jupyter notebook, using the built-in data stream Javascript engine.

## src/cl/visualisation/jupyter.py

- `def display_visualiser(javascript_file: str | Path, html_file: str | Path | None = None, data_streams: list[str] | None = None, use_sidebar: bool = True, aspect_ratio: float | None = None)`
  - Display a custom visualiser in a Jupyter notebook.
- `def show_activity(mode: Literal['2d', '3d'] = '2d', use_sidebar: bool = True, focus_on_channels: int | Sequence[int] | ChannelSet | None = None, **kwargs)`
  - Show the activity visualiser in a Jupyter notebook, supporting both 2D and 3D modes.
