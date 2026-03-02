# Cortical Labs API Quick Reference

## Core runtime

- Session lifecycle: `cl.open(take_control=True, wait_until_recordable=True)`
- Main interface object: `Neurons`
- Real-time loop: `neurons.loop(ticks_per_second=..., stop_after_seconds=... | stop_after_ticks=...)`
- Timestamp/data access: `neurons.timestamp()`, `neurons.read(frame_count, from_timestamp=None)`

## Stimulation

- Immediate stimulation: `neurons.stim(channel_set, stim_design, burst_design=None, lead_time_us=80)`
- Related operations: `interrupt`, `interrupt_then_stim`, `sync`
- Types:
  - `ChannelSet(...)`
  - `StimDesign(...)`
  - `BurstDesign(count, frequency_hz)`
  - `StimPlan` via `neurons.create_stim_plan()`

## Recording and streams

- Start recording: `neurons.record(...) -> Recording`
- Recording controls: `stop`, `has_stopped`, `wait_until_stopped`, `set_attribute`, `update_attributes`
- Data streams: `neurons.create_data_stream(name, attributes=None) -> DataStream`
- Stream updates: `append(timestamp, data)`, `set_attribute`, `update_attributes`

## Offline analysis

- Load recording: `RecordingView("/path/file.h5")`
- Core data: `samples`, `spikes`, `stims`, `attributes`, `data_streams`
- Analysis helpers:
  - `analyse_firing_stats`
  - `analyse_network_bursts`
  - `analyse_criticality`
  - `analyse_information_entropy`
  - `analyse_lempel_ziv_complexity`
  - `analyse_dct_features`
  - `analyse_spike_triggered_histogram`
  - `analyse_functional_connectivity`

## App workflow CLI

- Scaffold app: `python -m cl.app.init [target_directory]`
- Package app: `python -m cl.app.pack [target_directory]`
- Local run: `python -m cl.app.run <target_directory> <config.json>`
- Playback recording: `python -m cl.playback <recording_file.h5> [app_directory]`

## High-value guardrails from docs

- Prefer `cl.open()` context manager over direct `Neurons` instantiation.
- Loop jitter can raise `TimeoutError` on CL1 if per-iteration work exceeds time budget.
- `cl.app.model` documents stimulation constraints:
  - amplitude `(0.0, 3.0]` microamps
  - pulse width in 20 microsecond increments
  - non-stimmable channels: `0, 4, 7, 56, 63`
