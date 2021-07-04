import discord
from discord.ext import commands


class TCHelp(commands.DefaultHelpCommand):
    def __init__(self) -> None:
        super().__init__()
        self.commands_heading = "指令:"
        self.no_category = "其他指令"

    def get_ending_note(self):
        command_name = self.invoked_with
        return (
            f"使用 {self.context.prefix}{command_name} [指令名稱] 來獲取個別指令的詳細用法\n"
            f"你也可以使用 {self.context.prefix}{command_name} [類別名稱] 來獲取每個類別的資訊"
        )