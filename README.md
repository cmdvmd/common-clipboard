<img src="logo.png" alt="Common Clipboard logo" height align="right"/>

# Common Clipboard

Welcome to Common Clipboard, an application written with Python to create a shared clipboard experience between iOS and
Windows devices connected to a common network. This shared clipboard allows for easier and faster data transfer between
the two platforms, where data copied on one device can almost instantly be pasted in the other. This project is intended
to be similar to Apple's [Universal Clipboard](https://support.apple.com/en-us/HT209460) that creates a shared clipboard
between Apple products. Common Clipboard interfaces with the native clipboard of the device it is running on, meaning
all the data transfer happens in the background, so the only commands you need to know are copy and paste!
> **Note:** Currently only works for the transfer of unicode text and images

## Usage

Common Clipboard runs in the background on both Windows (as a systray icon) and iOS (as a Shortcut). When new data is
copied on one device, it will automatically be copied on the other devices connected to the server. The Common Clipboard
Server must be run on a Windows Computer as a separate application.

## Installation

### Windows

Download the latest version of the Common Clipboard and Common Clipboard Server applications
from [releases](https://github.com/cmdvmd/common-clipboard/releases)

### iOS

Download the latest version of the Common Clipboard shortcut from [RoutineHub](https://routinehub.co/shortcut/16222/) as
well as the [Scriptable app](https://apps.apple.com/app/id1405459188).
> **Note:** A Windows device running Common Clipboard Server is required for the shortcut to run

## Credits

Credit to [Airwave](https://github.com/thura10/airwave) by thura10 for the inspiration and the server finding code for
this project
