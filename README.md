# GitHub Codespaces ♥️ Flask

Welcome to your shiny new Codespace running Flask! We've got everything fired up and running for you to explore Flask.

You've got a blank canvas to work on from a git perspective as well. There's a single initial commit with the what you're seeing right now - where you go from here is up to you!

Everything you do here is contained within this one codespace. There is no repository on GitHub yet. If and when you’re ready you can click "Publish Branch" and we’ll create your repository and push up your project. If you were just exploring then and have no further need for this code then you can simply delete your codespace and it's gone forever.

To run this application:

```
flask --debug run
```

## Using pipenv to manage your virtual environment (instructions written for mac)

Note: You can link your pipenv environment with an ide like Pycharm  
The pipenv Python interpreter is stored in `~/.local/share/virtualenvs`  
Never install packages through the IDE, still use the pipenv command in the terminal (fact check this)
###Link with more information
https://realpython.com/pipenv-guide/#pipenv-introduction

### Install pipenv locally

In your source code root directory:

    $ pip install pipenv

### Activating the virtual environment

In your source code root directory:

    $ pipenv shell

### lock environment (do this before committing)

    $ pipenv lock

### Deactivating the virtual environment

Do this when you woul dlike to leave the virtual environment:

    $ deactivate

### Updating the virtual environment

This will download any new dependancies added in version controll.

    $ pipenv install

### Install a new package

Use this to install new packages. This will update the Pipenv file for version control.

    $ pipenv install <package_name>
