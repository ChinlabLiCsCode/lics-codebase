# Notes on LabVIEW → Labscript Conversion

Labscript sequences are Python files that define a sequence. An empty template is shown in `lics-labscript-apparatus/conv_example.py`. The process of converting a LabVIEW sequence to a Labscript sequence is similar to the `seq_dump` function, with the changes described below.

---

## Section-by-Section Process

### 1. Python Header
Add Python imports and other header material (see `conv_example.py`).

### 2. LabVIEW `seq_dump` Header
Include the original LabVIEW `seq_dump` header as a comment block.

### 3. Channel List
Comment out the channel list, but keep it visible. Add an extra column mapping each channel's LabVIEW name to its Labscript name:

- Use `NI_channel_map.csv` to map old NI channel names (e.g. `3.1_Dual_1064_Int_Lock`) to new ones (e.g. `Dual_1064_Int_Lock__b4c16`).
- The **"OG Ch"** and **"Full"** columns are the most precise identifiers for original and new channels, respectively.
- Full Python names for new channels are defined in `connection_table.py`.
- For channels **not** carried over from the old NI system, add a note in this section where appropriate.
- **2.x and 7.x channels are defunct** — they were duplicate output boxes and are not present in the new system. Treat them as "no new channel" regardless of any apparent name similarity to channels that do exist.

### 4. Procedure List
Comment out the procedure list. Express all times in the format `(value_in_ms)e-3` — i.e. write the numeric value in milliseconds followed by `e-3`. For example, 11700 ms → `11700e-3`. This applies to all times throughout the script (procedure start times, event offsets, ramp durations).

### 5. 655xx Code List
This should be **functional Python code**. For each code, write:

```python
code_655xx = <current_value>
```

Include the rest of the table as comments below each definition.

### 6. Sequence Start
Add code to start the sequence:

1. Call `start()`.
2. Set `t = 1e-6` and **set all mapped channels to their LabVIEW init values** at `t` (see channel list). For analog channels use `constant(t, value)`; for digital channels use `go_high(t)` or `go_low(t)` based on whether the init value is ≥ 2.5 V. For channels governed by Zeeman logic, emit the five `Zeeman_C*` `constant()` calls based on the initial 1.31/1.32 state.
3. Add a time marker and wait for the **60 Hz line trigger** (see `conv_example.py`).

### 7. Procedures (One by One)
For each procedure:

1. Add a comment with the procedure name.
2. Set `t = <procedure_time_in_seconds>`.
3. Add a time marker at that time using the procedure name as the marker label.
4. For each channel command, translate into Labscript syntax relative to `t`:

#### a. Digital Channels
| LabVIEW | Labscript |
|---------|-----------|
| Jump to `0` | `go_low()` |
| Jump to `5` | `go_high()` |

#### b. Analog Channels
| LabVIEW | Labscript |
|---------|-----------|
| Jump to value | `constant()` |

#### c. Analog Ramps
- FINE ramps → `ramp()` with `samplerate=FAST_FREQ`
- COARSE ramps → `ramp()` with `samplerate=SLOW_FREQ`

> **Ramp timing note:** LabVIEW ramps are defined by their *end time* (start inferred from the previous command). Labscript ramps are defined by a *start time and duration*.
>
> To convert:
> 1. Find the **previous command** on that channel.
> 2. Comment it out with a note: `# replaced by ramp at t = [time] in proc [procedure]`
> 3. Program the Labscript `ramp()` using that previous command's time as the start.

#### d. 655xx Codes
- If a code appears as a **time**: use `code_655xx / 1000` (convert ms → s).
- If a code appears as a **voltage**: use `code_655xx` directly.
- Codes may appear as procedure times or as times within a procedure.

#### e. Disabled Procedures
Write the code as normal, but **comment out the entire procedure block**.

### 8. Sequence End
After all procedures:

1. Set `t` to **1 ms after the latest absolute event time** across all enabled procedures. The latest absolute event time is `max(procedure_time + event_offset)` over all enabled procedures and their enabled events.
2. **Set all mapped channels back to their LabVIEW init values** at `t` (same logic as Section 6 step 2).
3. Call `stop(t)`.

---

## Special Cases

### 8a. Labscript Name Overrides
The following channels use **overridden names** (no `bxcxx` suffix):

| NI Channel | Labscript Name |
|------------|----------------|
| `3.0_N_V_AH` | `Bitter_V_AH` |
| `3.7_N_V_HH` | `Bitter_V_HH` |
| `5.13_Bias_1/2_AH_-x` | `Bias_X_AH` |
| `5.12_Bias_1/2_HH_x` | `Bias_X_HH` |
| `5.14_Bias_3/4_AH_-y` | `Bias_Y_AH` |
| `5.15_Bias_3/4_HH_y` | `Bias_Y_HH` |
| `5.16_Bias_5/6_AH_z` | `Bias_Z_AH` |
| `5.17_Bias_5/6_HH_-z` | `Bias_Z_HH` |

### 8b. Zeeman Channel Logic
Digital channels `1.31_Cs_Li_Zeswitch` and `1.32_ZCurrents` are **not continued** in the new system. Instead, five analog channels must switch their value based on the state of `1.31` and `1.32`.

**The five analog channels:**
- `Zeeman_C1__b4c10`
- `Zeeman_C2__b4c11`
- `Zeeman_C3__b4c12`
- `Zeeman_C4__b4c13`
- `Zeeman_C5__b4c14`

**Logic table:**

| `1.32` state | `1.31` state | Analog channel values |
|-------------|-------------|----------------------|
| `0` | — | All five channels → `0` |
| `5` | `0` | Cs MOT Zeeman currents: `ZEEMAN_C1_CS`, `ZEEMAN_C2_CS`, … |
| `5` | `5` | Li MOT Zeeman currents: `ZEEMAN_C1_LI`, `ZEEMAN_C2_LI`, … |

> **Rule:** Any time `1.31` **or** `1.32` is changed, check the state of the other channel and insert the appropriate `constant()` commands for all five Zeeman channels.