# RfSoC Interaction Handler

Generic interface for interacting with the RfSoC.

## API Calls

### `InteractionHandler(ip_address)`
Creates an instance of the handler. Needs the IP address of the RfSoC to connect.

**Parameters:**
- `ip_address` *(str)* — IP address of the RfSoC.

---

### `send_message(instruction, par)`
Sends a command message with the given instruction and parameter.

**Parameters:**
- `instruction` *(str)* — The instruction to be sent.  
- `par` *(int)* — The parameter to send with the instruction.

---

### `send_start()`
Starts the streaming engines of the RfSoC.  
Depending on the trigger setting it either:
- starts sending and generates a trigger, or  
- waits for an incoming trigger.

---

### `send_stop()`
Stops the streaming engines and the DACs.

---

### `send_set_trigger_in()`
Configures the RfSoC to **receive** a trigger.

---

### `send_set_trigger_out()`
Configures the RfSoC to **send out** a trigger.

---

### `send_data(filepath)`
Sends a signal file to the board and stores it in the database.  
The filename will be used for saving the file on the RfSoC.

**Parameters:**
- `filepath` *(str)* — Path to the file that should be sent.

---

### `select_signal(channel_id, filename)`
Selects the signal for a given channel from a filename.  
The file must be uploaded to the RfSoC first. Otherwise, this will throw an error.

**Parameters:**
- `channel_id` *(int)* — Channel ID to use (`0–7`).  
- `filename` *(str)* — Name of the signal file to be loaded.

---

### `list_files()`
Prints a list with all files that are uploaded. The location on the RfSoC and the 
creation time is given.

---

### `delete_signal(filename)`
Deletes the file from the database and from the drive.

**Parameters:**
- `filename` *(str)* — Name of the signal file to be deleted.

### `set_freq(frequency)`
Sets the sampling frequency of the DACs. Due to clock divider issues some frequencies are
not allowed but currently there is no sanity check (will be added in the future). The
maximum frequency is 168.75hz (for now).

**Parameters:**
- `frequency` *(int)* — The target frequency in Hz 

### `set_sending_mode(mode)`
Sets the sending mode of the RfSoC. Currently it can be toggled between sending a single
transmission and stream out periodically.

**Parameters:**
- `mode` *(int)* — Allows changing between two modes for now: 
                    0 -- Stream Mode
                    1 -- Single Transmission mode
