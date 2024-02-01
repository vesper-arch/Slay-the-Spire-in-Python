# Slay-The-Spire-in-Python
A text-based version of Slay the Spire coded in python

DISCLAIMER: I am not a professional, if you wonder why the code kinda sucks, that's why.

## Missing features(as of current release)
+ Currently you can only play as the Ironclad.
+ Potions exist but you can't use them.
+ Most boss relics aren't implemented.
+ Only Act 1 is available.
+ Shops and Merchants don't exist.
+ Most Curses don't do anything.
+ There is no saving.

### Download:
The game currently only has a Windows version.


## VSCode Dev Environment

If using VSCode, there is a devcontainer that can be used to get up and running quickly.  This will install all the dependencies and allow you to run the game.

Quick Start:
  - Install [VSCode](https://code.visualstudio.com/)
  - Install [Docker](https://www.docker.com/)
  - Install [Devcontainer](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) VSCode Extension
  - Open the project in VSCode
  - Click the green button in the bottom left corner of VSCode
  - Select `Dev Container: Reopen in Container`
  - Wait for the container to build
  - Open a terminal in VSCode
  - Run `./scripts/play.sh` to start the game or `./scripts/test.sh` to run the tests
