# The Minecraft Server Plugin
McExchange has two parts, the aws lambda backend and a plugin for modded minecraft servers (The plugin was developed on [Spigot](https://www.spigotmc.org/)).
This plugin lives here :)

## Install Guide
I hope that I can get Docker-based setup running for this mess, but until then, you'll have to result to running in locally.

## Prerequisites
You'll need a running JRE installed, according to Minecraft's server-docs, any version between 16-19 should work.

1. Create a new directory for your server, and download [Spigot's BuildTools](https://hub.spigotmc.org/jenkins/job/BuildTools/lastSuccessfulBuild/artifact/target/BuildTools.jar)
2. Running the tools via `java -jar BuildTools.jar` starts the installation process for spigot.
3. Once that's done, you can start spigot via `java -jar spigot-x.xx.x.jar`
4. When your start the server for the first time, it will create a eula.txt file and exit
5. Change the content of that file from `eula=false` to `eula=TRUE`
6. Now you can start the server again and it should properly initialize and start - you can shut it down again
7. Install the [minecraft-python](https://github.com/Macuyiko/minecraft-python) plugin (download the latest release and copy the jar into the `/plugin` directory )
8. Now start the server again, multiple directories should be created `python` and `lib-common` -> this means the plugin is working
9. Make a new directory `python-plugins`, copy the `exchange.py` script there and you're good to go.
10. If you start the server and connect to it in Minecraft, you can type `/exchange` in the chat to check if it's working

For simplicity sake, you can just set up the server in this directory, the gitignore is configured in a way, that no files from the sever itself will be included by it.
Then you also don't need to copy/create the `python-plugins` folder.


## Configuration
To make the plugin talk to the lambda function, the corresponding url needs to be put into the plugin itself.
Change `api_base_url` to the url of your deployed lambda function and you're ready!

## Known Issues
- Autocomplete is not working for the commands - but this is an issue with [minecraft-python](https://github.com/Macuyiko/minecraft-python) itself and not this plugin.