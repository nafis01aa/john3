import re
import inspect

class bcommands:
    prefix = [
        '/',
        '.',
        ',',
        '!'
    ]

    def __init__(
        self
    ):
        self.start = self.cmd("start")  # Start the bot
        self.help = self.cmd("help") # Get instructions
        self.cancel = self.cmd("cancel") # Cancel a forward task
        self.plans = self.cmd("plans") # Get bot paid plans
        self.profile = self.cmd("profile") # Get my profile
        self.thumbnails = self.cmd("thumbnails") # Set or change thumbnail of content
        self.remove_thumbnail = self.cmd("rmthumb") # Remove existing thumbnail
        self.login = self.cmd("login") # Login my account
        self.logout = self.cmd("logout") # Logout my (logined) account

        self.cancel_menu = "Cancel ❌"
        self.forward_menu = r"https?:\/\/t\.me\/\S+"

    def cmd(self, text):
        prefix_pattern = r"[" + re.escape(''.join(self.prefix)) + r"]"
        return r"^" + prefix_pattern + rf"{text}(?:\s.*|@[^ ]*|$)"

    def get(self, mode):
        return self._get_cmd(getattr(self, mode, ''))

    def _get_cmd(self, command_value):
        match = re.match(r"^[^\w]*([\w]+)", command_value)
        if match:
            return match.group(1)
        return None

    def get_bot_commands(self):
        source_lines = inspect.getsourcelines(self.__class__)[0]
        commands = []

        for name, value in inspect.getmembers(self):
            if not name.startswith("__") and not name.endswith("_menu"):
                for line in source_lines:
                    if f"self.{name} =" in line:
                        command_name = self._get_cmd(value)
                        if command_name:
                            note = None
                            if "#" in line:
                                note = line.split("#")[1].strip()
                            if note is None:
                                note = "Bot command!"
                            commands.append((command_name, note))
                            break

        commands.sort(key=lambda x: (x[0] != 'start', x[0]))
        return commands

class acommands:
    prefix = [
        '/',
        '.',
        ',',
        '!'
    ]

    def __init__(
        self
    ):
        self.restart = self.cmd("restart") # Restart
        self.broadcast = self.cmd("broadcast") # Restart
        self.logs = self.cmd("log") # Restart
        self.promote = self.cmd("promote") # Restart
        self.demote = self.cmd("demote") # Restart
        self.task_info = self.cmd("tinfo") # Restart

    def cmd(self, text):
        prefix_pattern = r"[" + re.escape(''.join(self.prefix)) + r"]"
        return r"^" + prefix_pattern + rf"{text}(?:\s.*|@[^ ]*|$)"

    def get(self, mode):
        return self._get_cmd(getattr(self, mode, ''))

    def _get_cmd(self, command_value):
        match = re.match(r"^[^\w]*([\w]+)", command_value)
        if match:
            return match.group(1)
        return None

    def get_bot_commands(self):
        source_lines = inspect.getsourcelines(self.__class__)[0]
        commands = []

        for name, value in inspect.getmembers(self):
            if not name.startswith("__") and not name.endswith("_menu"):
                for line in source_lines:
                    if f"self.{name} =" in line:
                        command_name = self._get_cmd(value)
                        if command_name:
                            note = None
                            if "#" in line:
                                note = line.split("#")[1].strip()
                            if note is None:
                                note = "Bot command!"
                            commands.append((command_name, note))
                            break

        commands.sort(key=lambda x: (x[0] != 'start', x[0]))
        return commands

admin_command = acommands()
command = bcommands()