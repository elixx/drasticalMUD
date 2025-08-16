#!/usr/bin/env python3
import curses
import asyncio
import threading
import time
import queue
import re
import argparse
import sys
from collections import deque
import telnetlib3

class ANSIParser:
    """Parse ANSI escape sequences and convert them to curses color pairs"""
    
    def __init__(self):
        # ANSI color codes to curses color mapping
        self.ansi_to_curses = {
            30: curses.COLOR_BLACK,
            31: curses.COLOR_RED,
            32: curses.COLOR_GREEN,
            33: curses.COLOR_YELLOW,
            34: curses.COLOR_BLUE,
            35: curses.COLOR_MAGENTA,
            36: curses.COLOR_CYAN,
            37: curses.COLOR_WHITE,
            # Bright colors (treated as bold)
            90: curses.COLOR_BLACK,
            91: curses.COLOR_RED,
            92: curses.COLOR_GREEN,
            93: curses.COLOR_YELLOW,
            94: curses.COLOR_BLUE,
            95: curses.COLOR_MAGENTA,
            96: curses.COLOR_CYAN,
            97: curses.COLOR_WHITE,
        }
        
        # Background color mapping
        self.ansi_bg_to_curses = {
            40: curses.COLOR_BLACK,
            41: curses.COLOR_RED,
            42: curses.COLOR_GREEN,
            43: curses.COLOR_YELLOW,
            44: curses.COLOR_BLUE,
            45: curses.COLOR_MAGENTA,
            46: curses.COLOR_CYAN,
            47: curses.COLOR_WHITE,
            # Bright background colors
            100: curses.COLOR_BLACK,
            101: curses.COLOR_RED,
            102: curses.COLOR_GREEN,
            103: curses.COLOR_YELLOW,
            104: curses.COLOR_BLUE,
            105: curses.COLOR_MAGENTA,
            106: curses.COLOR_CYAN,
            107: curses.COLOR_WHITE,
        }
        
        # Track current state
        self.current_fg = -1  # Default foreground
        self.current_bg = -1  # Default background
        self.bold = False
        self.dim = False
        self.underline = False
        
        # Color pair cache
        self.color_pairs = {}
        self.next_pair_id = 10  # Start after reserved pairs
        
        # ANSI escape sequence regex
        self.ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    
    def get_color_pair(self, fg, bg, bold=False):
        """Get or create a curses color pair for the given colors"""
        key = (fg, bg, bold)
        if key not in self.color_pairs:
            # Check if curses is properly initialized and has color pairs
            max_pairs = getattr(curses, 'COLOR_PAIRS', 64)  # Default fallback
            if self.next_pair_id < max_pairs and curses.has_colors():
                try:
                    curses.init_pair(self.next_pair_id, fg, bg)
                    self.color_pairs[key] = self.next_pair_id
                    self.next_pair_id += 1
                except curses.error:
                    # Fallback to default colors if color pair creation fails
                    return 0
            else:
                # Fallback to default colors if we run out of pairs
                return 0
        return self.color_pairs[key]
    
    def parse_ansi_sequence(self, sequence):
        """Parse a single ANSI escape sequence and update state"""
        if not sequence.startswith('\x1B[') or not sequence.endswith('m'):
            return
        
        # Extract the parameters
        params_str = sequence[2:-1]  # Remove \x1B[ and m
        if not params_str:
            params = [0]  # Default to reset
        else:
            try:
                params = [int(p) if p else 0 for p in params_str.split(';')]
            except ValueError:
                return
        
        i = 0
        while i < len(params):
            code = params[i]
            
            if code == 0:  # Reset
                self.current_fg = -1
                self.current_bg = -1
                self.bold = False
                self.dim = False
                self.underline = False
            elif code == 1:  # Bold
                self.bold = True
            elif code == 2:  # Dim
                self.dim = True
            elif code == 4:  # Underline
                self.underline = True
            elif code == 22:  # Normal intensity (not bold/dim)
                self.bold = False
                self.dim = False
            elif code == 24:  # Not underlined
                self.underline = False
            elif code in self.ansi_to_curses:  # Foreground color
                self.current_fg = self.ansi_to_curses[code]
                if code >= 90:  # Bright colors
                    self.bold = True
            elif code in self.ansi_bg_to_curses:  # Background color
                self.current_bg = self.ansi_bg_to_curses[code]
            elif code == 39:  # Default foreground
                self.current_fg = -1
            elif code == 49:  # Default background
                self.current_bg = -1
            
            i += 1
    
    def parse_text(self, text):
        """Parse text with ANSI sequences and return list of (text, attributes) tuples"""
        if not text:
            return []
        
        result = []
        last_end = 0
        
        for match in self.ansi_escape.finditer(text):
            # Add text before this escape sequence
            if match.start() > last_end:
                plain_text = text[last_end:match.start()]
                if plain_text:
                    attrs = self.get_current_attributes()
                    result.append((plain_text, attrs))
            
            # Process the escape sequence
            sequence = match.group(0)
            if sequence.endswith('m'):  # SGR (Select Graphic Rendition)
                self.parse_ansi_sequence(sequence)
            
            last_end = match.end()
        
        # Add remaining text
        if last_end < len(text):
            plain_text = text[last_end:]
            if plain_text:
                attrs = self.get_current_attributes()
                result.append((plain_text, attrs))
        
        return result
    
    def get_current_attributes(self):
        """Get current curses attributes based on ANSI state"""
        try:
            color_pair = self.get_color_pair(self.current_fg, self.current_bg, self.bold)
            attrs = curses.color_pair(color_pair)
            
            if self.bold:
                attrs |= curses.A_BOLD
            if self.dim:
                attrs |= curses.A_DIM
            if self.underline:
                attrs |= curses.A_UNDERLINE
            
            return attrs
        except (AttributeError, curses.error):
            # Fallback if curses is not initialized or has issues
            attrs = 0
            if self.bold:
                attrs |= getattr(curses, 'A_BOLD', 0)
            if self.dim:
                attrs |= getattr(curses, 'A_DIM', 0)
            if self.underline:
                attrs |= getattr(curses, 'A_UNDERLINE', 0)
            return attrs

class MUDClient:
    def __init__(self):
        self.reader = None
        self.writer = None
        self.connected = False
        self.host = ""
        self.port = 0
        self.history = deque(maxlen=100)  # Store last 100 commands
        self.message_queue = queue.Queue()
        self.loop = None
        self.connection_task = None
        
    async def connect_async(self, host, port):
        """Connect to the MUD server asynchronously"""
        try:
            self.reader, self.writer = await telnetlib3.open_connection(host, port)
            self.connected = True
            self.host = host
            self.port = port
            return True
        except Exception as e:
            return False, str(e)
    
    def connect(self, host, port):
        """Connect to the MUD server (sync wrapper)"""
        if self.loop and not self.loop.is_closed():
            future = asyncio.run_coroutine_threadsafe(
                self.connect_async(host, port), self.loop
            )
            try:
                return future.result(timeout=10)
            except Exception as e:
                return False, str(e)
        return False, "Event loop not available"
    
    async def disconnect_async(self):
        """Disconnect from the MUD server asynchronously"""
        if self.writer:
            self.writer.close()
            if hasattr(self.writer, 'wait_closed'):
                await self.writer.wait_closed()
        self.connected = False
        self.reader = None
        self.writer = None
    
    def disconnect(self):
        """Disconnect from the MUD server (sync wrapper)"""
        if self.loop and not self.loop.is_closed():
            future = asyncio.run_coroutine_threadsafe(
                self.disconnect_async(), self.loop
            )
            try:
                future.result(timeout=5)
            except Exception:
                pass
        self.connected = False
    
    async def send_command_async(self, command):
        """Send a command to the MUD server asynchronously"""
        if self.connected and self.writer:
            try:
                self.writer.write(command + "\r\n")
                await self.writer.drain()
                # Add to history if it's not empty and not the same as last command
                if command.strip() and (not self.history or command != self.history[-1]):
                    self.history.append(command)
                return True
            except Exception as e:
                self.connected = False
                return False, f"Send error: {e}"
        return False
    
    def send_command(self, command):
        """Send a command to the MUD server (sync wrapper)"""
        if self.loop and not self.loop.is_closed():
            future = asyncio.run_coroutine_threadsafe(
                self.send_command_async(command), self.loop
            )
            try:
                return future.result(timeout=5)
            except Exception as e:
                return False, f"Command send timeout/error: {e}"
        return False, "Event loop not available"
    
    async def read_data_async(self):
        """Read data from the MUD server asynchronously"""
        if self.connected and self.reader:
            try:
                # Try to read some data with a short timeout
                try:
                    data = await asyncio.wait_for(self.reader.read(8192), timeout=0.01)
                    return data
                except asyncio.TimeoutError:
                    return ""
            except Exception as e:
                self.connected = False
        return ""
    
    async def connection_handler(self):
        """Handle the connection in the event loop"""
        while self.connected:
            try:
                data = await self.read_data_async()
                if data:
                    self.message_queue.put(data)
                await asyncio.sleep(0.01)
            except Exception:
                self.connected = False
                break

class MUDInterface:
    def __init__(self, auto_connect_host=None, auto_connect_port=None):
        self.client = MUDClient()
        self.output_lines = deque(maxlen=1000)  # Store last 1000 lines as (text_segments, raw_text) tuples
        self.input_buffer = ""
        self.current_prompt = ""  # Store the detected prompt
        self.history_pos = 0
        self.scroll_pos = 0
        self.event_loop_thread = None
        self.error_queue = queue.Queue()  # Queue for errors from background threads
        self.ansi_parser = ANSIParser()
        self.needs_redraw = True  # Track if screen needs redrawing
        self.last_output_count = 0  # Track changes to output
        self.last_connection_status = False  # Track connection changes
        self.auto_connect_host = auto_connect_host
        self.auto_connect_port = auto_connect_port
        
        # Prompt detection patterns - common MUD prompt formats
        self.prompt_patterns = [
            r'^[>\$#%] ?$',  # Simple prompts: >, $, #, %
            r'^[A-Za-z]+ ?[>\$#%] ?$',  # Name followed by prompt: Player >
            r'^\[[^\]]*\] ?[>\$#%] ?$',  # Bracketed info: [100/100hp] >
            r'^\d+h(?:\d+m)?(?:\d+mv)? ?[>\$#%] ?$',  # HP/Mana/Move: 100h50m25mv >
            r'^<[^>]*> ?$',  # Angle bracket prompts: <100hp>
            r'^\([^\)]*\) ?[>\$#%] ?$',  # Parenthetical prompts: (Ready) >
            r'^\w+@\w+ ?[>\$#%] ?$',  # User@host style: player@mud >
            r'^[A-Za-z]+:#\d+> ?$',  # FOOB:#12456> style prompts
            r'^[A-Za-z0-9_-]+:#\d+> ?$',  # Extended character names with numbers/underscores
            r'^.+:#\d+> ?$',  # Any text followed by :#number>
        ]
        
        # Disable debug mode by default
        self.debug_prompts = False
        
    def start_event_loop(self):
        """Start the asyncio event loop in a separate thread"""
        def run_loop():
            try:
                self.client.loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self.client.loop)
                self.client.loop.run_forever()
            except Exception as e:
                self.error_queue.put(f"Event loop error: {e}")
        
        self.event_loop_thread = threading.Thread(target=run_loop, daemon=True)
        self.event_loop_thread.start()
        time.sleep(0.1)  # Give the loop time to start
    
    def stop_event_loop(self):
        """Stop the asyncio event loop"""
        try:
            if self.client.loop and not self.client.loop.is_closed():
                self.client.loop.call_soon_threadsafe(self.client.loop.stop)
        except Exception as e:
            self.error_queue.put(f"Error stopping event loop: {e}")
    
    def init_curses(self, stdscr):
        """Initialize curses settings"""
        curses.curs_set(1)  # Show cursor
        curses.noecho()     # Don't echo keys automatically
        curses.cbreak()     # React to keys immediately
        stdscr.keypad(True) # Enable special keys
        stdscr.nodelay(True) # Make getch() non-blocking
        
        # Initialize colors if available
        if curses.has_colors():
            curses.start_color()
            curses.use_default_colors()
            curses.init_pair(1, curses.COLOR_CYAN, -1)    # Status line
            curses.init_pair(2, curses.COLOR_GREEN, -1)   # Connected status
            curses.init_pair(3, curses.COLOR_RED, -1)     # Disconnected status
    
    def draw_interface(self, stdscr):
        """Draw the main interface"""
        height, width = stdscr.getmaxyx()
        
        # Only clear and redraw if needed
        if not self.needs_redraw:
            return
            
        # Clear screen only when necessary
        stdscr.clear()
        
        # Draw title bar
        title = "Python MUD Client (telnetlib3)"
        status = f" | Connected to {self.client.host}:{self.client.port}" if self.client.connected else " | Not connected"
        title_line = title + status
        
        stdscr.addstr(0, 0, title_line[:width-1], curses.color_pair(1) | curses.A_BOLD)
        stdscr.addstr(1, 0, "=" * (width-1), curses.color_pair(1))
        
        # Draw output area
        output_height = height - 5  # Leave space for input area
        output_start = 2
        
        # Calculate which lines to show based on scroll position
        total_lines = len(self.output_lines)
        start_line = max(0, total_lines - output_height - self.scroll_pos)
        end_line = min(total_lines, start_line + output_height)
        
        for i, line_num in enumerate(range(start_line, end_line)):
            if line_num < len(self.output_lines):
                text_segments, raw_line = self.output_lines[line_num]
                try:
                    self.draw_colored_line(stdscr, output_start + i, 0, text_segments, width - 1)
                except curses.error:
                    pass  # Ignore errors from writing to bottom-right corner
        
        # Draw input area
        input_y = height - 3
        stdscr.addstr(input_y, 0, "=" * (width-1), curses.color_pair(1))
        
        # Display the prompt if we have one, otherwise use default >
        prompt_text = self.current_prompt if self.current_prompt else "> "
        # Ensure prompt ends with a space for clean appearance
        if prompt_text and not prompt_text.endswith(' '):
            prompt_text += " "
        
        # Parse and display the prompt with colors
        if self.current_prompt:
            prompt_segments = self.ansi_parser.parse_text(prompt_text)
            current_x = 0
            for text, attrs in prompt_segments:
                try:
                    stdscr.addstr(input_y + 1, current_x, text, attrs)
                    current_x += len(text)
                except curses.error:
                    break
            # Add the input buffer after the prompt
            try:
                stdscr.addstr(input_y + 1, current_x, self.input_buffer)
                cursor_x = min(current_x + len(self.input_buffer), width - 1)
            except curses.error:
                cursor_x = width - 1
        else:
            # No prompt detected, use simple display
            stdscr.addstr(input_y + 1, 0, prompt_text + self.input_buffer)
            cursor_x = min(len(prompt_text) + len(self.input_buffer), width - 1)
        
        # Draw help line
        help_text = "/connect host port | /disconnect | /quit | /help"
        stdscr.addstr(height - 1, 0, help_text[:width-1], curses.color_pair(1))
        
        # Position cursor at end of input
        stdscr.move(input_y + 1, cursor_x)
        
        stdscr.refresh()
        self.needs_redraw = False  # Reset redraw flag
    
    def draw_colored_line(self, stdscr, y, x, text_segments, max_width):
        """Draw a line with colored text segments"""
        current_x = x
        
        for text, attrs in text_segments:
            if current_x >= x + max_width:
                break  # Don't exceed line width
            
            # Truncate text if it would exceed the line width
            available_width = x + max_width - current_x
            if len(text) > available_width:
                text = text[:available_width]
            
            if text:  # Only draw if there's text to display
                try:
                    stdscr.addstr(y, current_x, text, attrs)
                    current_x += len(text)
                except curses.error:
                    # Stop drawing if we hit an error (like screen boundary)
                    break
    
    def handle_input(self, key):
        """Handle keyboard input"""
        self.needs_redraw = True  # Any input requires redraw
        if key == curses.KEY_UP:
            # Navigate history up
            if self.client.history and self.history_pos < len(self.client.history):
                if self.history_pos == 0:
                    self.saved_input = self.input_buffer
                self.history_pos += 1
                self.input_buffer = self.client.history[-self.history_pos]
        
        elif key == curses.KEY_DOWN:
            # Navigate history down
            if self.history_pos > 0:
                self.history_pos -= 1
                if self.history_pos == 0:
                    self.input_buffer = getattr(self, 'saved_input', '')
                else:
                    self.input_buffer = self.client.history[-self.history_pos]
        
        elif key == curses.KEY_PPAGE:  # Page Up
            self.scroll_pos = min(self.scroll_pos + 10, len(self.output_lines))
        
        elif key == curses.KEY_NPAGE:  # Page Down
            self.scroll_pos = max(self.scroll_pos - 10, 0)
        
        elif key == ord('\n') or key == ord('\r'):
            # Send command or handle slash command
            if self.input_buffer.strip():
                # Check if it's a slash command
                if self.input_buffer.strip().startswith('/'):
                    self.add_output(f"> {self.input_buffer}")
                    result = self.handle_slash_command(self.input_buffer)
                    if result == "quit":
                        self.input_buffer = ""
                        return False  # Quit the application
                else:
                    # Regular MUD command
                    result = self.client.send_command(self.input_buffer)
                    if result is True:
                        self.add_output(f"> {self.input_buffer}")
                    else:
                        # Handle error result
                        if isinstance(result, tuple) and len(result) == 2:
                            error_msg = result[1]
                        else:
                            error_msg = "Not connected to server"
                        self.add_output(f"Error: {error_msg}")
            self.input_buffer = ""
            self.history_pos = 0
            self.scroll_pos = 0  # Auto-scroll to bottom on new input
        
        elif key == curses.KEY_BACKSPACE or key == 127 or key == 8:
            # Backspace
            if self.input_buffer:
                self.input_buffer = self.input_buffer[:-1]
                self.history_pos = 0
        
        elif key == 21:  # Ctrl+U (kill line)
            # Clear the entire input buffer
            self.input_buffer = ""
            self.history_pos = 0
        
        elif key == 23:  # Ctrl+W (kill word)
            # Remove the last word from the input buffer
            if self.input_buffer:
                # Find the end of the current word (skip trailing spaces)
                i = len(self.input_buffer) - 1
                while i >= 0 and self.input_buffer[i].isspace():
                    i -= 1
                # Find the beginning of the word
                while i >= 0 and not self.input_buffer[i].isspace():
                    i -= 1
                # Keep everything up to the beginning of the word
                self.input_buffer = self.input_buffer[:i + 1]
                self.history_pos = 0
        
        elif 32 <= key <= 126:  # Printable characters
            self.input_buffer += chr(key)
            self.history_pos = 0
        
        return True
    
    def detect_prompt(self, text):
        """Detect if the given text looks like a MUD prompt"""
        # Remove ANSI codes for pattern matching
        clean_text = self.ansi_parser.ansi_escape.sub('', text).strip()
        
        # Debug output to see what we're trying to match
        if self.debug_prompts and clean_text:
            self.add_debug_output(f"[DEBUG] Checking potential prompt: '{clean_text}'")
        
        for i, pattern in enumerate(self.prompt_patterns):
            if re.match(pattern, clean_text):
                if self.debug_prompts:
                    self.add_debug_output(f"[DEBUG] Prompt matched pattern {i+1}: {pattern}")
                return True
        
        # If no patterns match but it's short and ends with common prompt characters, it might still be a prompt
        if len(clean_text) < 50 and clean_text.endswith(('>', '$', '#', '%')):
            if self.debug_prompts:
                self.add_debug_output(f"[DEBUG] Potential prompt by fallback rules: '{clean_text}'")
            return True
            
        return False
    
    def add_debug_output(self, text):
        """Add debug text to output buffer (separate from normal add_output to avoid recursion)"""
        text_segments = [(text, curses.color_pair(1))]  # Use cyan color for debug
        self.output_lines.append((text_segments, text))
        self.needs_redraw = True
    
    def add_output(self, text):
        """Add text to the output buffer with ANSI color support"""
        # Split text into lines and add each line
        lines = text.split('\n')
        for i, line in enumerate(lines):
            clean_line = line.rstrip('\r')
            
            # Check if this looks like a prompt
            # Only check the last line of multi-line text, and only if it's short
            is_last_line = (i == len(lines) - 1)
            if is_last_line and len(clean_line.strip()) > 0 and len(clean_line.strip()) < 50:
                if self.detect_prompt(clean_line):
                    # This looks like a prompt - store it and don't add to output
                    self.current_prompt = clean_line
                    self.needs_redraw = True
                    continue
            
            # Parse ANSI sequences and store both parsed segments and raw text
            text_segments = self.ansi_parser.parse_text(clean_line)
            if not text_segments:
                # If no ANSI codes, store as plain text
                text_segments = [(clean_line, 0)]
            self.output_lines.append((text_segments, clean_line))
        self.needs_redraw = True  # Mark for redraw when new content is added
    
    def check_error_queue(self):
        """Check for errors from background threads and display them"""
        while True:
            try:
                error_msg = self.error_queue.get_nowait()
                self.add_output(f"ERROR: {error_msg}")
            except queue.Empty:
                break
    
    def handle_slash_command(self, command):
        """Handle slash commands like /connect and /quit"""
        parts = command.strip().split()
        if not parts:
            return False
        
        cmd = parts[0].lower()
        
        if cmd in ["/quit", "/q"]:
            return "quit"
        
        elif cmd in ["/connect", "/c"]:
            if len(parts) >= 3:
                try:
                    host = parts[1]
                    port = int(parts[2])
                    self.add_output(f"Connecting to {host}:{port}...")
                    result = self.client.connect(host, port)
                    if result is True:
                        self.add_output(f"Connected to {host}:{port}")
                        # Start the connection handler
                        if self.client.loop:
                            self.client.connection_task = asyncio.run_coroutine_threadsafe(
                                self.client.connection_handler(), self.client.loop
                            )
                    else:
                        error_msg = result[1] if isinstance(result, tuple) else 'Unknown error'
                        self.add_output(f"Failed to connect to {host}:{port}: {error_msg}")
                except ValueError:
                    self.add_output("Error: Port must be a number")
                except Exception as e:
                    self.add_output(f"Error: {e}")
            else:
                self.add_output("Usage: /connect <host> <port>")
                self.add_output("Example: /connect localhost 4000")
        
        elif cmd in ["/disconnect", "/d"]:
            self.client.disconnect()
            self.add_output("Disconnected from server.")
        
        elif cmd in ["/help", "/h"]:
            self.show_help()
        
        elif cmd in ["/debug"]:
            self.debug_prompts = not self.debug_prompts
            status = "enabled" if self.debug_prompts else "disabled"
            self.add_output(f"Prompt debugging {status}")
        
        else:
            self.add_output(f"Unknown command: {cmd}")
            self.add_output("Available commands: /connect <host> <port>, /disconnect, /quit, /debug, /help")
        
        return True
    
    def show_help(self):
        """Display help information"""
        self.add_output("=== MUD Client Help ===")
        self.add_output("Slash Commands:")
        self.add_output("  /connect <host> <port>  - Connect to MUD server")
        self.add_output("  /disconnect             - Disconnect from server")
        self.add_output("  /debug                  - Toggle prompt detection debug mode")
        self.add_output("  /quit                   - Exit the client")
        self.add_output("  /help                   - Show this help")
        self.add_output("")
        self.add_output("Keyboard Shortcuts:")
        self.add_output("  Up/Down arrows          - Command history")
        self.add_output("  Page Up/Down            - Scroll output")
        self.add_output("  Ctrl+U                  - Kill entire input line")
        self.add_output("  Ctrl+W                  - Kill previous word")
        self.add_output("")
        self.add_output("Short forms: /c = /connect, /d = /disconnect, /q = /quit, /h = /help")
        self.add_output("")
        self.add_output("The client automatically detects server prompts and displays them")
        self.add_output("in the input bar. Use /debug to see what's being detected.")
    
    def read_server_data(self):
        """Read data from server message queue"""
        while True:
            try:
                # Process multiple messages at once to reduce update frequency
                messages = []
                try:
                    # Collect up to 10 messages or until queue is empty
                    for _ in range(10):
                        data = self.client.message_queue.get_nowait()
                        if data:
                            messages.append(data)
                except queue.Empty:
                    pass
                
                # Add all messages at once
                if messages:
                    combined_data = ''.join(messages)
                    self.add_output(combined_data)
                    
            except Exception as e:
                self.error_queue.put(f"Error reading server data: {e}")
                time.sleep(1)  # Wait before retrying after error
            time.sleep(0.05)  # Increased delay to reduce CPU usage and flicker
    
    def run(self, stdscr):
        """Main application loop"""
        self.init_curses(stdscr)
        
        # Start the asyncio event loop
        self.start_event_loop()
        
        # Start background thread for reading server data
        reader_thread = threading.Thread(target=self.read_server_data, daemon=True)
        reader_thread.start()
        
        self.add_output("Python MUD Client started (using telnetlib3).")
        self.add_output("Use slash commands: /connect <host> <port>, /disconnect, /quit, /help")
        self.add_output("Use Up/Down arrows to navigate command history.")
        self.add_output("Use Page Up/Down to scroll through output.")
        
        # Auto-connect if host and port were provided
        if self.auto_connect_host and self.auto_connect_port:
            self.add_output(f"Auto-connecting to {self.auto_connect_host}:{self.auto_connect_port}...")
            result = self.client.connect(self.auto_connect_host, self.auto_connect_port)
            if result is True:
                self.add_output(f"Connected to {self.auto_connect_host}:{self.auto_connect_port}")
                # Start the connection handler
                if self.client.loop:
                    self.client.connection_task = asyncio.run_coroutine_threadsafe(
                        self.client.connection_handler(), self.client.loop
                    )
            else:
                error_msg = result[1] if isinstance(result, tuple) else 'Unknown error'
                self.add_output(f"Failed to connect: {error_msg}")
        
        running = True
        while running:
            try:
                # Check for errors from background threads
                self.check_error_queue()
                
                # Check if connection status changed
                if self.client.connected != self.last_connection_status:
                    self.needs_redraw = True
                    self.last_connection_status = self.client.connected
                
                # Only draw if something changed
                self.draw_interface(stdscr)
                
                key = stdscr.getch()
                if key != -1:  # Key was pressed
                    running = self.handle_input(key)
                    
            except KeyboardInterrupt:
                running = False
            except Exception as e:
                # Display any curses-related errors in the interface
                self.add_output(f"Interface error: {e}")
                time.sleep(0.1)  # Brief pause to prevent rapid error loops
            
            time.sleep(0.05)  # Increased delay to reduce CPU usage and flicker
        
        # Cleanup
        try:
            self.client.disconnect()
            self.stop_event_loop()
        except Exception as e:
            self.add_output(f"Cleanup error: {e}")

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Python MUD Client with telnetlib3",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Start client without connecting
  %(prog)s localhost 4000     # Connect to localhost:4000
  %(prog)s mud.example.com 23 # Connect to remote MUD
        """
    )
    parser.add_argument('host', nargs='?', help='MUD server hostname or IP address')
    parser.add_argument('port', nargs='?', type=int, help='MUD server port number')
    return parser.parse_args()

def main():
    """Main entry point"""
    args = parse_args()
    
    # Validate arguments
    if (args.host and not args.port) or (args.port and not args.host):
        print("Error: Both host and port must be provided together", file=sys.stderr)
        sys.exit(1)
    
    interface = MUDInterface(args.host, args.port)
    
    try:
        curses.wrapper(interface.run)
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        # Try to display error in interface first, then fall back to print
        try:
            interface.add_output(f"FATAL ERROR: {e}")
            time.sleep(2)  # Give time to see the error
        except:
            pass
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
