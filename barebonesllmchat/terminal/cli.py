import curses
from enum import Enum

import requests
import json
from time import sleep

import sys
import pathlib
sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))
import common
from common.chat_history import CHAT_ROLE, ChatHistory
from terminal.interface import ChatbotClient

class FOCUS(Enum):
    API_KEY = 0
    CHAT_SELECTOR = 1
    CHAT_BUTTONS = 2
    CHAT_MESSAGES = 3
    ROLE_SELECTOR = 4
    PROMPT = 5


###################################
#                                 #
# WIP                             #
#                                 #
###################################


class ChatbotCLI:
    def __init__(self, base_url):
        self.api_key = ""
        self.chat_client = ChatbotClient(base_url, self.api_key)
        self.current_chat_id = None
        self.selected_role = "USER"
        self.message_input = ""
        self.current_focus = FOCUS.API_KEY
        self.chats = ["brave-eagl", "brave-cact", "bright-her", "lively-jag", "fearless-h", "eager-eagl"]
        self.messages = []
        self.chat_index = 0
        self.message_scroll_offset = 0
        self.button_selected = "Create"  # Initial selection for buttons

    def main(self, stdscr):
        curses.curs_set(0)
        curses.start_color()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_GREEN)
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_GREEN)

        stdscr.refresh()
        curses.resizeterm(*stdscr.getmaxyx())

        while True:
            stdscr.clear()
            self.draw_interface(stdscr)
            stdscr.refresh()

            key = stdscr.getch()
            if key == 9:  # Tab key to switch focus
                self.current_focus = FOCUS((self.current_focus.value + 1) % 6)
            elif key == curses.KEY_UP:
                self.navigate_up()
            elif key == curses.KEY_DOWN:
                self.navigate_down()
            elif key == curses.KEY_LEFT:
                self.navigate_left()
            elif key == curses.KEY_RIGHT:
                self.navigate_right()
            elif key in [10, 13]:  # Enter key action
                self.enter_key_action()
            elif key == 27:  # Escape key to exit
                break
            else:
                self.handle_text_input(key)

    def draw_interface(self, stdscr):
        height, width = stdscr.getmaxyx()
        height -= 2  # Safe margin to prevent out-of-bounds errors
        width -= 2

        # Draw API Key Box
        self.draw_box(stdscr, "API Key:", 0, 0, 3, width, focus=self.current_focus == FOCUS.API_KEY)
        stdscr.addstr(1, 2, self.api_key[:width - 4], curses.color_pair(1))

        # Draw Chat Selector
        self.draw_box(stdscr, "Chats:", 3, 0, 4, width, focus=self.current_focus == FOCUS.CHAT_SELECTOR)
        self.draw_chat_selector(stdscr, width)

        # Draw "Create new chat" and "Delete selected chat" buttons under chat selector
        self.draw_chat_buttons(stdscr, width)

        # Draw Chat Messages
        self.draw_box(stdscr, "Chat Messages:", 9, 0, height - 18, width, focus=self.current_focus == FOCUS.CHAT_MESSAGES)
        self.draw_chat_messages(stdscr, width)

        # Role Selector with Side-by-Side Boxes
        self.draw_role_selector(stdscr, height, width)

        # Message Input Box with increased height
        self.draw_box(stdscr, "Your Message:", height - 5, 0, 5, width, focus=self.current_focus == FOCUS.PROMPT)
        stdscr.addstr(height - 4, 2, self.message_input[:width - 4], curses.color_pair(1))

    def draw_box(self, stdscr, title, y, x, height, width, focus=False):
        color = curses.color_pair(2 if focus else 1)
        stdscr.attron(color)

        # Draw top border with title
        stdscr.addstr(y, x, f"{'_' * (width - 1)}", color)

        # Draw left and right vertical borders, and the bottom border
        for line in range(1, height - 1):
            stdscr.addstr(y + line, x, "|", color)
            stdscr.addstr(y + line, x + width - 2, "|", color)
        stdscr.addstr(y, x + 2, title[:width - 4], color)
        stdscr.addstr(y + height - 1, x, "_" * (width - 1), color)  # Bottom border
        stdscr.attroff(color)

    def draw_chat_selector(self, stdscr, width):
        max_chats_display = 3
        display_chats = [self.chats[i] for i in range(self.chat_index, min(len(self.chats), self.chat_index + max_chats_display))]
        chat_y = 5

        for i, chat in enumerate(display_chats):
            style = curses.color_pair(3) if (i + self.chat_index) == self.chat_index else curses.color_pair(1)
            stdscr.addstr(chat_y, 2 + i * (width // max_chats_display), chat.ljust(width // max_chats_display)[:width // max_chats_display], style)

    def draw_chat_buttons(self, stdscr, width):
        # Position for the buttons
        button_y = 7
        button_height = 3
        button_width = width - 2  # Full width for the button box

        # Draw button box
        self.draw_box(stdscr, "Chat Actions:", button_y, 0, button_height, button_width, focus=self.current_focus == FOCUS.CHAT_BUTTONS)

        # Style for "Create new chat" button
        create_color = curses.color_pair(3) if self.button_selected == "Create" else curses.color_pair(1)
        stdscr.addstr(button_y + 1, 2, "[ Create new chat ]", create_color)

        # Style for "Delete selected chat" button
        delete_color = curses.color_pair(3) if self.button_selected == "Delete" else curses.color_pair(1)
        stdscr.addstr(button_y + 1, button_width // 2 + 2, "[ Delete selected chat ]", delete_color)



    def draw_chat_messages(self, stdscr, width):
        max_lines = curses.LINES - 20
        visible_messages = self.messages[self.message_scroll_offset:self.message_scroll_offset + max_lines]
        for i, message in enumerate(visible_messages):
            wrapped_message = f"{message['role']}: {message['content'][:width - 4]}"
            stdscr.addstr(10 + i, 2, wrapped_message, curses.color_pair(1))

    def draw_role_selector(self, stdscr, height, width):
        system_box_x = 2
        user_box_x = width // 2 + 1

        # Style for SYSTEM box
        system_color = curses.color_pair(3) if self.selected_role == "SYSTEM" else curses.color_pair(1)
        stdscr.addstr(height - 6, system_box_x, "[ SYSTEM ]", system_color)

        # Style for USER box
        user_color = curses.color_pair(3) if self.selected_role == "USER" else curses.color_pair(1)
        stdscr.addstr(height - 6, user_box_x, "[ USER ]", user_color)

    def handle_text_input(self, key):
        if self.current_focus == FOCUS.API_KEY:
            #if key in [10, 13] and self.api_key.strip():
            #    self.chat_client.set_api_key(self.api_key)
            if key in [curses.KEY_BACKSPACE, 127]:
                self.api_key = self.api_key[:-1]
            else:
                self.api_key += chr(key)
        elif self.current_focus == FOCUS.PROMPT:
            #if key in [10, 13] and self.message_input.strip():
            #    self.send_message()
            if key in [curses.KEY_BACKSPACE, 127]:
                self.message_input = self.message_input[:-1]
            else:
                self.message_input += chr(key)

    def navigate_up(self):
        if self.current_focus == FOCUS.CHAT_MESSAGES:
            self.message_scroll_offset = max(0, self.message_scroll_offset - 1)

    def navigate_down(self):
        if self.current_focus == FOCUS.CHAT_MESSAGES:
            self.message_scroll_offset = min(len(self.messages) - 10, self.message_scroll_offset + 1)

    def navigate_left(self):
        if self.current_focus == FOCUS.CHAT_SELECTOR:
            self.chat_index = max(0, self.chat_index - 1)
        elif self.current_focus == FOCUS.CHAT_BUTTONS:  # Buttons area
            self.button_selected = "Create" if self.button_selected == "Delete" else "Delete"
        elif self.current_focus == FOCUS.ROLE_SELECTOR:
            self.selected_role = "SYSTEM" if self.selected_role == "USER" else "USER"

    def navigate_right(self):
        if self.current_focus == FOCUS.CHAT_SELECTOR:
            self.chat_index = min(len(self.chats) - 1, self.chat_index + 1)
        elif self.current_focus == FOCUS.CHAT_BUTTONS:  # Buttons area
            self.button_selected = "Create" if self.button_selected == "Delete" else "Delete"
        elif self.current_focus == FOCUS.ROLE_SELECTOR:
            self.selected_role = "SYSTEM" if self.selected_role == "USER" else "USER"

    def enter_key_action(self):
        if self.current_focus == FOCUS.CHAT_BUTTONS:  # Button area
            if self.button_selected == "Create":
                self.create_chat()
            elif self.button_selected == "Delete":
                self.delete_chat()
        elif self.current_focus == FOCUS.API_KEY:
            if self.api_key.strip():
                self.chat_client.set_api_key(self.api_key)
                print("Set api key")
        elif self.current_focus == FOCUS.PROMPT:
            if self.message_input.strip():
                self.send_message()
        #elif self.current_focus == FOCUS.ROLE_SELECTOR:
        #    self.selected_role = "SYSTEM" if self.selected_role == "USER" else "USER"

    def send_message(self):
        self.chat_client.send_message(self.current_chat_id, self.message_input, role=self.selected_role)
        #self.load_chat_messages()
        self.message_input = ""

    def create_chat(self):
        # Placeholder for create chat logic
        self.chat_client.create_chat()

        #self.chats.append(f"chat-{len(self.chats) + 1}")
        #self.chat_index = len(self.chats) - 1  # Focus on the new chat

    def delete_chat(self):
        # Placeholder for delete chat logic
        self.chat_client.delete_chat(self.chats[self.chat_index])


        #if self.chats:
        #    del self.chats[self.chat_index]
        #    self.chat_index = max(0, self.chat_index - 1)

    def run(self):
        curses.wrapper(self.main)

if __name__ == "__main__":
    chatbot_cli = ChatbotCLI("http://localhost:5000")
    chatbot_cli.run()