# Ulauncher Snippet Search

Search a local text file by keyword, then type the selected snippet into the focused application.

## Requirements

- Ulauncher with support for extension API `^2.0.0`.
- `xdotool` installed and available on `PATH`. On Debian or Ubuntu-based systems, install it with `sudo apt install xdotool`.
- An X11 session. `xdotool` may not work in a native Wayland session.

The extension uses Python's standard library and Ulauncher's bundled extension API. No additional Python packages are required.

## Setup

The extension directory should be located at:

```text
~/.local/share/ulauncher/extensions/com.github.enjaychang.ulauncher-snippet-search/
```

After installing or changing the extension files, restart Ulauncher or reload its extensions. In Ulauncher preferences, set **Snippets file** to the path of your snippets file. The default is:

```text
~/.config/snippet-search/snippets.txt
```

The extension keyword defaults to `s`; it can also be changed in Ulauncher preferences.

## Snippet Format

Put one snippet on each line. Separate the searchable keywords from the text to insert with ` : ` (a space, colon, and space):

```text
vpn/network : systemctl restart NetworkManager
ticket/jira : Hello, could you please take a look at this issue?
```

Search matches case-insensitive substrings in the text before the first ` : ` only. A slash is just part of the keyword text, so searching for `network` matches the first example. The text after the first separator is inserted as-is; additional ` : ` sequences in the snippet text are preserved. Blank lines are ignored, and lines without the separator are skipped.

## Usage

1. Focus the destination application and place the cursor where the snippet should go.
2. Open Ulauncher and type `s ` followed by a keyword, for example `s network`.
3. Select a result and press Enter. The Ulauncher window closes and the snippet is typed into the destination application.

Typing only `s ` lists all valid snippets. The displayed result is the keyword field; the snippet text is not searched or shown in the result list.

## Troubleshooting

- **No results:** Check that the configured file is readable and that each entry uses the exact ` : ` separator.
- **Unable to read snippets file:** Check the file path and read permissions in Ulauncher preferences.
- **The selected text is not typed:** Confirm `xdotool` is installed and available on `PATH`, and that the session is X11 rather than native Wayland.