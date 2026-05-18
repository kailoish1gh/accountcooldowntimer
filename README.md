# ⚡ Account Cooldown Tracker

Welcome to your premium **Account Cooldown Tracker**! This is a real-time, terminal-based dashboard that lets you monitor, add, and reset cooldowns on multiple accounts in a single central hub.

It uses custom ANSI high-contrast colors, double-line panels, dynamic graphical progress bars, and zero screen flicker.

---

## 🚀 How to Launch the Tracker

### On Windows (Recommended):
Simply double-click the **`run.bat`** file inside the `acctimers` folder on your Desktop. 
It will automatically open a formatted Command Prompt / Windows Terminal window and start the application instantly!

*Alternatively, you can open PowerShell or Command Prompt, navigate to this folder, and run:*
```powershell
python cooldown_tracker.py
```

---

## ⌨️ Shortcut Key Bindings

While the tracker is running, it listens to your keystrokes **in real time**. You do **not** need to press Enter to run commands:

| Key | Action | Description |
|:---:|:---|:---|
| **`A`** | **Add Account** | Launches the interactive wizard to add account nickname, days, and hours. You can add multiple accounts sequentially! |
| **`D`** | **Delete Account** | Prompts for the list index number to remove an account permanently. |
| **`R`** | **Reset Cooldown** | Restarts a cooldown using either its original duration or a newly defined length. |
| **`C`** | **Clear Ready** | Sweeps all finished (`READY!`) accounts off the screen to keep your dashboard clean. |
| **`Q`** | **Quit App** | Restores your terminal window cursor and exits the program cleanly. |

---

## 💎 Elite Features Included

1. **Anti-Flicker Technology**: Instead of wiping the console screen (which causes blinding white flashes), the app utilizes smooth ANSI terminal cursor-resets (`\033[H`).
2. **Accurate Counting & Persistence**: All account timer durations, creations, and targets are saved in `cooldowns.json` under standard epoch values. Even if you close the terminal or restart your computer, it keeps counting down accurately!
3. **Double-Tone Alarm Notification**: When an account cooldown reaches completion, the app will emit a pleasant double-tone sound (`880Hz -> 1200Hz`) exactly once to alert you that it is `READY!`.
4. **Interactive Entry Loop**: When adding new timers, it prompts you at the end of the entry: *`Add another account? (y/n) [n]: `*, letting you sequentially add multiple accounts with ease.
5. **Dynamic Progress Bars**: The visual grid calculates the exact percentage elapsed since you started/reset the cooldown, rendering a colorful filled graphical bar (`[████░░░░░░]`) that turns solid green once complete.

---

### 📂 Configuration File Details

- **File**: `cooldowns.json` (located in the same folder as the script)
- **Format**:
```json
{
  "accounts": [
    {
      "nick": "MainAccount",
      "created_timestamp": 1779012345.0,
      "target_timestamp": 1779141945.0,
      "duration_seconds": 129600,
      "alerted": false
    }
  ]
}
```
You can inspect, share, or edit this file manually at any time!
