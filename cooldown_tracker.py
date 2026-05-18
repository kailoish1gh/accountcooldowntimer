import os
import sys
import time
import json
import datetime
import threading

# Global variables for terminal styling (ANSI codes)
C_RESET = "\033[0m"
C_BOLD = "\033[1m"
C_DIM = "\033[2m"

# Colors
C_CYAN = "\033[36m"
C_MAGENTA = "\033[35m"
C_YELLOW = "\033[33m"
C_GREEN = "\033[32m"
C_RED = "\033[31m"
C_BLUE = "\033[34m"

# Bold/Bright Colors
C_B_CYAN = "\033[1;96m"
C_B_MAGENTA = "\033[1;95m"
C_B_YELLOW = "\033[1;93m"
C_B_GREEN = "\033[1;92m"
C_B_RED = "\033[1;91m"
C_B_WHITE = "\033[1;97m"

# Standard screen width
TERM_WIDTH = 80

# Windows ANSI Support & Beep sound initialization
msvcrt = None
winsound = None

if sys.platform == 'win32':
    import msvcrt
    import ctypes
    # Trigger Windows Terminal Virtual Processing (ANSI Escapes)
    os.system('')
    try:
        kernel32 = ctypes.windll.kernel32
        hStdOut = kernel32.GetStdHandle(-11) # STD_OUTPUT_HANDLE
        mode = ctypes.c_ulong()
        kernel32.GetConsoleMode(hStdOut, ctypes.byref(mode))
        mode.value |= 4 # ENABLE_VIRTUAL_TERMINAL_PROCESSING
        kernel32.SetConsoleMode(hStdOut, mode)
    except Exception:
        pass
    
    try:
        import winsound
    except ImportError:
        winsound = None

# Configuration file location
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cooldowns.json")

def load_accounts():
    """Load accounts from the json config file."""
    if not os.path.exists(CONFIG_FILE):
        return []
    try:
        with open(CONFIG_FILE, "r") as f:
            data = json.load(f)
            # Default backward compatibility
            return data.get("accounts", [])
    except Exception:
        return []

def save_accounts(accounts):
    """Save accounts to the json config file."""
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump({"accounts": accounts}, f, indent=2)
    except Exception as e:
        # Silently fail or write error to log if needed
        pass

def trigger_beep():
    """Trigger a nice, double-tone non-blocking beep on Windows."""
    if winsound:
        def beep_thread():
            try:
                winsound.Beep(880, 120)
                time.sleep(0.04)
                winsound.Beep(1200, 200)
            except Exception:
                pass
        threading.Thread(target=beep_thread, daemon=True).start()

def get_terminal_header(title):
    """Draw a beautiful double-line header panel."""
    # Outer width: 80 chars
    # Border characters: ╔ ═ ╗ ║ ╚ ╝
    inner_width = 78
    title_colored = f"{C_B_CYAN}{title.center(inner_width)}{C_RESET}"
    border_color = C_CYAN
    
    header = []
    header.append(f"{border_color}╔" + "═" * inner_width + f"╗{C_RESET}")
    header.append(f"{border_color}║{title_colored}{border_color}║{C_RESET}")
    header.append(f"{border_color}╚" + "═" * inner_width + f"╝{C_RESET}")
    return "\n".join(header)

def make_progress_bar(percentage, is_ready):
    """Draw a sleek progress bar of exactly 10 blocks inside brackets [████░░░░░░]."""
    bar_width = 10
    if is_ready:
        percentage = 1.0
    filled = int(round(percentage * bar_width))
    empty = bar_width - filled
    
    if is_ready:
        bar = f"{C_B_GREEN}" + "█" * filled + f"{C_RESET}"
    else:
        # Gradient or simple colored progress
        if percentage < 0.33:
            color = C_RED
        elif percentage < 0.75:
            color = C_YELLOW
        else:
            color = C_CYAN
        bar = f"{color}" + "█" * filled + f"{C_DIM}" + "░" * empty + f"{C_RESET}"
        
    return f"[{bar}]"

def format_timestamp(epoch):
    """Convert epoch float to local readable timestamp format."""
    dt = datetime.datetime.fromtimestamp(epoch)
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def add_account_flow():
    """Run an interactive wizard to add one or multiple accounts."""
    while True:
        # Clear screen for wizard
        sys.stdout.write("\033[2J\033[H")
        sys.stdout.flush()
        
        print(get_terminal_header("ADD NEW COOLDOWN TIMERS"))
        print(f"\n{C_B_WHITE}Please enter account details below:{C_RESET}\n")
        
        # 1. Nickname
        accounts = load_accounts()
        existing_nicks = {acc["nick"].lower() for acc in accounts}
        
        while True:
            nick = input(f"{C_B_CYAN}➤ Account Nickname: {C_RESET}").strip()
            if not nick:
                print(f"{C_B_RED}⚠ Nickname cannot be empty.{C_RESET}")
                continue
            if nick.lower() in existing_nicks:
                print(f"{C_B_RED}⚠ An account with nickname '{nick}' already exists.{C_RESET}")
                continue
            break
            
        # 2. Cooldown Duration Days
        while True:
            days_str = input(f"{C_B_CYAN}➤ Cooldown Days    [0]: {C_RESET}").strip()
            if not days_str:
                days = 0
                break
            try:
                days = int(days_str)
                if days < 0:
                    raise ValueError()
                break
            except ValueError:
                print(f"{C_B_RED}⚠ Please enter a valid non-negative integer for days.{C_RESET}")
                
        # 3. Cooldown Duration Hours
        while True:
            hours_str = input(f"{C_B_CYAN}➤ Cooldown Hours   [0]: {C_RESET}").strip()
            if not hours_str:
                hours = 0
                break
            try:
                hours = int(hours_str)
                if hours < 0:
                    raise ValueError()
                break
            except ValueError:
                print(f"{C_B_RED}⚠ Please enter a valid non-negative integer for hours.{C_RESET}")

        # Compute times (Minutes are no longer prompted and default to 0)
        duration_seconds = (days * 86400) + (hours * 3600)
        if duration_seconds <= 0:
            print(f"\n{C_B_YELLOW}⚠ Cooldown duration is 0 seconds. It will be READY instantly.{C_RESET}")
            # Give it 0 duration, target = created
            duration_seconds = 0
            
        now = time.time()
        new_account = {
            "nick": nick,
            "created_timestamp": now,
            "target_timestamp": now + duration_seconds,
            "duration_seconds": duration_seconds,
            "alerted": False
        }
        
        accounts.append(new_account)
        save_accounts(accounts)
        
        print(f"\n{C_B_GREEN}✔ Successfully added '{nick}' with {days}d {hours}h cooldown!{C_RESET}")
        
        # Ask to move to the next account
        print(f"\n{C_DIM}────────────────────────────────────────────────────────────────────────{C_RESET}")
        another = input(f"{C_B_WHITE}Add another account? (y/n) [n]: {C_RESET}").strip().lower()
        if another != 'y':
            break

def delete_account_flow():
    """Prompt the user to delete a specific account by index."""
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()
    print(get_terminal_header("DELETE ACCOUNT TRACKER"))
    
    accounts = load_accounts()
    if not accounts:
        print(f"\n{C_B_YELLOW}⚠ No accounts to delete.{C_RESET}")
        time.sleep(1.5)
        return
        
    print(f"\n{C_B_WHITE}Current Accounts list:{C_RESET}\n")
    for i, acc in enumerate(accounts, 1):
        print(f"  {C_B_CYAN}[{i:02d}]{C_RESET} {acc['nick']}")
        
    print(f"\n{C_DIM}────────────────────────────────────────────────────────────────────────{C_RESET}")
    while True:
        idx_str = input(f"{C_B_WHITE}Enter the number (#) to delete (or Enter to Cancel): {C_RESET}").strip()
        if not idx_str:
            return
        try:
            idx = int(idx_str)
            if 1 <= idx <= len(accounts):
                deleted_nick = accounts[idx-1]["nick"]
                accounts.pop(idx-1)
                save_accounts(accounts)
                print(f"\n{C_B_GREEN}✔ Deleted '{deleted_nick}' successfully!{C_RESET}")
                time.sleep(1.2)
                return
            else:
                print(f"{C_B_RED}⚠ Index out of range.{C_RESET}")
        except ValueError:
            print(f"{C_B_RED}⚠ Please enter a valid number.{C_RESET}")

def reset_account_flow():
    """Prompt the user to reset the cooldown of a specific account."""
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()
    print(get_terminal_header("RESET ACCOUNT COOLDOWN"))
    
    accounts = load_accounts()
    if not accounts:
        print(f"\n{C_B_YELLOW}⚠ No accounts to reset.{C_RESET}")
        time.sleep(1.5)
        return
        
    print(f"\n{C_B_WHITE}Current Accounts list:{C_RESET}\n")
    for i, acc in enumerate(accounts, 1):
        # Format remaining time
        rem = acc["target_timestamp"] - time.time()
        status = f"{C_B_GREEN}READY!{C_RESET}" if rem <= 0 else f"{C_B_YELLOW}{int(rem//3600)} hours left{C_RESET}"
        print(f"  {C_B_CYAN}[{i:02d}]{C_RESET} {acc['nick']:<20} (Status: {status})")
        
    print(f"\n{C_DIM}────────────────────────────────────────────────────────────────────────{C_RESET}")
    while True:
        idx_str = input(f"{C_B_WHITE}Enter the number (#) to reset (or Enter to Cancel): {C_RESET}").strip()
        if not idx_str:
            return
        try:
            idx = int(idx_str)
            if 1 <= idx <= len(accounts):
                acc = accounts[idx-1]
                break
            else:
                print(f"{C_B_RED}⚠ Index out of range.{C_RESET}")
        except ValueError:
            print(f"{C_B_RED}⚠ Please enter a valid number.{C_RESET}")
            
    # Reset Choice
    print(f"\nResetting {C_B_WHITE}'{acc['nick']}'{C_RESET}...")
    orig_days = int(acc['duration_seconds'] // 86400)
    orig_hours = int((acc['duration_seconds'] % 86400) // 3600)
    opt = input(f"{C_B_CYAN}Reset with original duration? ({orig_days}d {orig_hours}h) (y/n) [y]: {C_RESET}").strip().lower()
    
    if opt == 'n':
        # Prompt new durations
        while True:
            days_str = input(f"{C_B_CYAN}➤ New Days    [0]: {C_RESET}").strip()
            if not days_str:
                days = 0
                break
            try:
                days = int(days_str)
                if days < 0: raise ValueError()
                break
            except ValueError:
                print(f"{C_B_RED}⚠ Invalid days.{C_RESET}")
                
        while True:
            hours_str = input(f"{C_B_CYAN}➤ New Hours   [0]: {C_RESET}").strip()
            if not hours_str:
                hours = 0
                break
            try:
                hours = int(hours_str)
                if hours < 0: raise ValueError()
                break
            except ValueError:
                print(f"{C_B_RED}⚠ Invalid hours.{C_RESET}")
                
        duration = (days * 86400) + (hours * 3600)
    else:
        duration = acc["duration_seconds"]
        
    now = time.time()
    acc["created_timestamp"] = now
    acc["target_timestamp"] = now + duration
    acc["duration_seconds"] = duration
    acc["alerted"] = False
    
    save_accounts(accounts)
    print(f"\n{C_B_GREEN}✔ Cooldown for '{acc['nick']}' has been reset!{C_RESET}")
    time.sleep(1.2)

def clear_ready_accounts():
    """Clear all accounts that are in the READY state to keep the workspace clean."""
    accounts = load_accounts()
    if not accounts:
        return
        
    now = time.time()
    active_accounts = [acc for acc in accounts if acc["target_timestamp"] - now > 0]
    cleared_count = len(accounts) - len(active_accounts)
    
    if cleared_count > 0:
        save_accounts(active_accounts)
        trigger_beep()
        print(f"\n{C_B_GREEN}✔ Cleared {cleared_count} ready account(s) from the list!{C_RESET}")
        time.sleep(1.0)

def main():
    """Main real-time UI render and keystroke handling loop."""
    # Hide the console cursor for cleaner drawing
    sys.stdout.write("\033[?25l")
    # Clear screen initially
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()
    
    last_beep_check_time = 0
    
    try:
        while True:
            # Check key presses non-blockingly
            if msvcrt and msvcrt.kbhit():
                try:
                    char = msvcrt.getch()
                    # Handle arrow keys or prefix characters
                    if char in (b'\x00', b'\xe0'):
                        msvcrt.getch() # Clear sub-buffer
                        continue
                    key = char.decode('utf-8', errors='ignore').lower()
                    
                    # Keyboard Routing
                    if key == 'q':
                        break
                    elif key == 'a':
                        # Show cursor for user inputs
                        sys.stdout.write("\033[?25h")
                        sys.stdout.flush()
                        add_account_flow()
                        # Hide cursor again
                        sys.stdout.write("\033[?25l")
                        sys.stdout.write("\033[2J\033[H")
                        sys.stdout.flush()
                    elif key == 'd':
                        sys.stdout.write("\033[?25h")
                        sys.stdout.flush()
                        delete_account_flow()
                        sys.stdout.write("\033[?25l")
                        sys.stdout.write("\033[2J\033[H")
                        sys.stdout.flush()
                    elif key == 'r':
                        sys.stdout.write("\033[?25h")
                        sys.stdout.flush()
                        reset_account_flow()
                        sys.stdout.write("\033[?25l")
                        sys.stdout.write("\033[2J\033[H")
                        sys.stdout.flush()
                    elif key == 'c':
                        clear_ready_accounts()
                        sys.stdout.write("\033[2J\033[H")
                        sys.stdout.flush()
                except Exception:
                    pass
            
            # Load accounts for this frame
            accounts = load_accounts()
            now = time.time()
            
            # Alarm and persistence checking:
            # We check if any account went to READY and beep once, then write to json.
            config_changed = False
            for acc in accounts:
                rem = acc["target_timestamp"] - now
                if rem <= 0 and not acc.get("alerted", False):
                    acc["alerted"] = True
                    config_changed = True
                    trigger_beep()
            if config_changed:
                save_accounts(accounts)
                
            # Move cursor back to top-left (0,0) smoothly
            sys.stdout.write("\033[H")
            
            # Render layout
            print(get_terminal_header("ACCOUNT COOLDOWN TRACKER"))
            
            # Print Shortcut Bar
            shortcuts_str = (
                f" Shortcuts: {C_B_CYAN}[A]{C_RESET} Add Account  "
                f"{C_B_CYAN}[D]{C_RESET} Delete  "
                f"{C_B_CYAN}[R]{C_RESET} Reset  "
                f"{C_B_CYAN}[C]{C_RESET} Clear Ready  "
                f"{C_B_RED}[Q]{C_RESET} Quit"
            )
            print(shortcuts_str)
            print(f"{C_DIM}─" * TERM_WIDTH + f"{C_RESET}")
            
            # Draw Table
            # Col widths: Col 1 (#) = 4, Col 2 (Nickname) = 20, Col 3 (Target Time) = 20, Col 4 (Progress) = 14, Col 5 (Remaining) = 16
            # Plus 4 separators + 2 borders = 80 characters total outer width.
            border_color = C_CYAN
            t_hdr = (
                f"{border_color}│{C_B_WHITE}  # {border_color}│"
                f"{C_B_WHITE} Account Nickname     {border_color}│"
                f"{C_B_WHITE} Target End Time     {border_color}│"
                f"{C_B_WHITE} Progress     {border_color}│"
                f"{C_B_WHITE} Time Left      {border_color}│{C_RESET}"
            )
            
            print(f"{border_color}┌───┬────────────────────┬────────────────────┬──────────────┬────────────────┐{C_RESET}")
            print(t_hdr)
            print(f"{border_color}├───┼────────────────────┼────────────────────┼──────────────┼────────────────┤{C_RESET}")
            
            if not accounts:
                empty_msg = "No accounts registered yet. Press [A] to add a new cooldown!".center(74)
                print(f"{border_color}│{C_DIM}{empty_msg}{border_color}│{C_RESET}")
            else:
                for idx, acc in enumerate(accounts, 1):
                    # Calculations
                    rem = acc["target_timestamp"] - now
                    duration = acc["duration_seconds"]
                    
                    if rem <= 0:
                        # READY!
                        ready = True
                        elapsed_pct = 1.0
                        time_left_str = "    READY!      "  # 16 chars
                        time_left_colored = f"{C_B_GREEN}{time_left_str}{C_RESET}"
                    else:
                        ready = False
                        # Progress pct
                        elapsed = now - acc["created_timestamp"]
                        elapsed_pct = (elapsed / duration) if duration > 0 else 1.0
                        elapsed_pct = max(0.0, min(1.0, elapsed_pct)) # Clamp between 0 and 1
                        
                        # Time breakdown
                        d_val = int(rem // 86400)
                        rem_day_sec = rem % 86400
                        h_val = int(rem_day_sec // 3600)
                        rem_hr_sec = rem_day_sec % 3600
                        m_val = int(rem_hr_sec // 60)
                        s_val = int(rem_hr_sec % 60)
                        
                        time_left_str = f" {d_val:02d}d {h_val:02d}h {m_val:02d}m {s_val:02d}s " # 16 chars
                        
                        # High visibility color for active cooldown
                        time_left_colored = f"{C_B_YELLOW}{time_left_str}{C_RESET}"
                        
                    # Format Nickname (20 chars max)
                    nick_raw = acc["nick"]
                    if len(nick_raw) > 18:
                        nick_disp = nick_raw[:15] + "..."
                    else:
                        nick_disp = nick_raw
                    nick_col = f" {nick_disp:<18} " # 20 chars
                    
                    # Target Time Format (20 chars)
                    target_time_raw = format_timestamp(acc["target_timestamp"])
                    target_col = f" {target_time_raw:<18} " # 20 chars
                    
                    # Row Index (4 chars)
                    idx_col = f" {idx:02d} "
                    
                    # Progress Bar (14 chars) -> make_progress_bar returns a 12-char bar (e.g. [██████░░░░])
                    # Centered inside the 14-char column
                    p_bar_content = make_progress_bar(elapsed_pct, ready)
                    p_bar_col = f" {p_bar_content} " # 14 chars outer (since make_progress_bar uses ANSI, we do manual alignment)
                    
                    # Draw actual columns
                    # We wrap them in colored borders
                    row_string = (
                        f"{border_color}│{C_RESET}{idx_col}{border_color}│"
                        f"{C_B_WHITE if ready else C_RESET}{nick_col}{border_color}│"
                        f"{C_DIM if ready else C_RESET}{target_col}{border_color}│"
                        f"{p_bar_col}{border_color}│"
                        f"{time_left_colored}{border_color}│{C_RESET}"
                    )
                    print(row_string)
                    
            print(f"{border_color}└───┴────────────────────┴────────────────────┴──────────────┴────────────────┘{C_RESET}")
            
            # Bottom status line
            print(f"\n{C_DIM} Status: [ Live - Updating at 2Hz ] [ Config: {os.path.basename(CONFIG_FILE)} ]{C_RESET}")
            
            # Wipe subsequent terminal spaces just in case the terminal shrank, to avoid trash characters
            sys.stdout.write("\033[J")
            sys.stdout.flush()
            
            # Refresh rate of ~0.5s for smooth countdown
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        pass
    finally:
        # Restore the console cursor before exiting
        sys.stdout.write("\033[?25h\033[2J\033[H")
        sys.stdout.flush()
        print(f"\n{C_B_CYAN}★ Thank you for using Account Cooldown Tracker! Goodbye! ★{C_RESET}\n")

if __name__ == "__main__":
    main()
