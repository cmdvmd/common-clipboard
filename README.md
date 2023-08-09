<img src="logo.png" alt="Common Clipboard logo" height align="right"/>

# Common Clipboard

Welcome to Common Clipboard, an application written with Python to create a shared clipboard experience between iOS and
Windows devices connected to a common network. This shared clipboard allows for easier and faster data transfer between
the two platforms, where data copied on one device can almost instantly be pasted in the other. This project is intended
to be similar to Apple's [Universal Clipboard](https://support.apple.com/en-us/HT209460) that creates a shared clipboard
between Apple products. Common Clipboard interfaces with the native clipboard of the device it is running on, meaning
all the data transfer happens in the background, so the only commands you need to know are copy and paste!
> **Note:** Currently only works for the transfer of unicode text and images and may have a short (1-2 second) delay
> depending on your internet speed

## Usage

### Windows

1. Run Common Clipboard Server on any **ONE** device on the local network
2. Run the Common Clipboard application on **ALL** desired devices on the local network
    * All devices will automatically connect to the server and begin sharing clipboard data over the local network
3. Both applications run in the background with no GUI, so open the system tray to close the applications when needed

> **Note:** Even if Common Clipboard Server is running on a device, the Common Clipboard application MUST be running for
> the shared clipboard experience to occur

### iOS/iPadOS

1. Ensure the Common Clipboard Server Application is running on any **ONE** Windows device on the local network
2. Run the Common Clipboard shortcut on **ALL** desired iOS/iPadOS devices on the local network
    * Just like in Windows, the shortcut will automatically connect to the server and begin sharing clipboard data with
      other connected devices
    * You may be repeatedly asked for permission to send copied data. This is a security feature by Apple and cannot be
      turned off. Simply click "Always Allow" when prompted
3. Close the Shortcuts app (press the home button or swipe up)
    * **DO NOT** quit the app by swiping it away from the menu. This will stop the shortcut

## Installation

### Windows

Download the latest version of the Common Clipboard and Common Clipboard Server applications
from [releases](https://github.com/cmdvmd/common-clipboard/releases)

### iOS

Download the latest version of the Common Clipboard shortcut from [RoutineHub](https://routinehub.co/shortcut/16222/) as
well as the [Scriptable app](https://apps.apple.com/app/id1405459188).

## Credits

Credit to [Airwave](https://github.com/thura10/airwave) by thura10 for the inspiration and the server finding code for
this project
