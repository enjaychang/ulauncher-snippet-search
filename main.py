# -*- coding: utf-8 -*-
import logging
import os
import subprocess
import time

from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import (
    ItemEnterEvent,
    KeywordQueryEvent,
    PreferencesEvent,
    PreferencesUpdateEvent,
)
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.item.ExtensionSmallResultItem import ExtensionSmallResultItem
from ulauncher.api.shared.action.DoNothingAction import DoNothingAction
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction


class SnippetSearchExtension(Extension):
    def __init__(self):
        super().__init__()
        self.snippet_file = os.path.expanduser(
            "~/.config/snippet-search/snippets.txt"
        )
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(PreferencesEvent, PreferencesLoadListener())
        self.subscribe(PreferencesUpdateEvent, PreferencesChangeListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())

    def search(self, query):
        results = []
        query = (query or "").strip().casefold()

        with open(self.snippet_file, "r", encoding="utf-8") as snippet_file:
            for line_number, raw_line in enumerate(snippet_file, start=1):
                line = raw_line.rstrip("\r\n")
                if not line:
                    continue

                keywords, separator, content = line.partition(" : ")
                if not separator:
                    logging.warning("Ignoring malformed snippet at line %d", line_number)
                    continue

                keywords = keywords.strip()
                if keywords and query in keywords.casefold():
                    results.append({"keywords": keywords, "content": content})

        return results


class PreferencesLoadListener(EventListener):
    def on_event(self, event, extension):
        extension.preferences.update(event.preferences)
        extension.snippet_file = os.path.expanduser(
            extension.preferences["snippet_file"]
        )


class PreferencesChangeListener(EventListener):
    def on_event(self, event, extension):
        if event.id == "snippet_file":
            extension.snippet_file = os.path.expanduser(event.new_value)


class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        query = event.get_argument() or ""
        try:
            results = extension.search(query)
        except (OSError, UnicodeError) as error:
            logging.error("Unable to read snippets file: %s", error)
            return RenderResultListAction(
                [
                    ExtensionResultItem(
                        icon="images/icon.png",
                        name="Unable to read snippets file",
                        on_enter=DoNothingAction(),
                    )
                ]
            )

        if not results:
            message = "No snippets found" if not query.strip() else "No matching snippets"
            return RenderResultListAction(
                [
                    ExtensionResultItem(
                        icon="images/icon.png",
                        name=message,
                        on_enter=DoNothingAction(),
                    )
                ]
            )

        return RenderResultListAction(
            [
                ExtensionSmallResultItem(
                    icon="images/icon.png",
                    name=result["keywords"],
                    on_enter=ExtensionCustomAction(result["content"]),
                )
                for result in results
            ]
        )


class ItemEnterEventListener(EventListener):
    def on_event(self, event, extension):
        content = event.get_data()
        if not isinstance(content, str):
            return

        time.sleep(0.2)
        subprocess.run(
            ["xdotool", "keyup", "ctrl", "alt", "Super_L", "Super_R"],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        try:
            subprocess.run(
                [
                    "xdotool",
                    "type",
                    "--delay",
                    "0",
                    "--clearmodifiers",
                    "--file",
                    "-",
                ],
                input=content,
                text=True,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except (OSError, subprocess.CalledProcessError) as error:
            logging.error("Unable to type selected snippet: %s", error)


if __name__ == "__main__":
    SnippetSearchExtension().run()