Envprobe
========

**Envprobe** (`envprobe`) is a shell hook tool that helps you manage your environment variables on a per-shell basis easily.
There is no need for clunky `export` sequences or manual `source`-ing of who-knows-where hand-written script files.

Envprobe was originally conceived as the tool between [shell `modules`](http://modules.sourceforge.net) and [`direnv`](http://direnv.net), but with added features such as saving your configuration on the fly.

- The [**full documentation**](http://envprobe.readthedocs.io/en/latest/index.html) is available on _Read the Docs_.
- [Installation](#installation)
  - [Dependencies](#dependencies)
  - [Download](#download)
  - [Hook](#hook)
- [Quick user guide](#quick-user-guide)
  - [Managing environment variables](#managing-environment-variables)
  - [Saved snapshots](#saved-snapshots)
  - [Type-safe access](#type-safe-access)
- [Configuring variable handling](#configuring-variable-handling)
  - [Obtaining variable type descriptions](#obtaining-variable-type-descriptions)

---

## Installation

### Dependencies

Envprobe is supplied as a no-tools-needed Python package.
The only things you need to have installed on the system are one of our supported POSIX-compliant shells and Python **3**.

Supported shells are reasonably modern versions of Bash and Zsh.

### Officially supported configurations

These are the configurations that the [CI](http://github.com/whisperity/Envprobe/actions) is running tests on:

| Operating system                     | Required dependencies | Shells supported                     |
|:-------------------------------------|:---------------------:|:-------------------------------------|
| Ubuntu 18.04 LTS (_Bionic Beaver_)   |    Python &ge; 3.6    | Bash (&ge; 4.4), Zsh (&ge; 5.4)      |
| Ubuntu 20.04 LTS (_Focal Fossa_)     |    Python &ge; 3.8    | Bash (&ge; 5.0), Zsh (&ge; 5.8)      |


### Download

You can download Envprobe's official releases from [PyPI](http://pypi.org/project/envprobe).

~~~{.sh}
pip install envprobe
~~~


#### From GitHub

You can also download Envprobe from the GitHub repository, either via `git` or in a tarball form.
Download the project anywhere you please, and extract the archive.
In this example, we'll use `~/envprobe` as the location.

~~~{.sh}
git clone http://github.com/whisperity/envprobe.git ~/envprobe \
    --origin upstream --single-branch --branch master --depth 1
~~~

or

~~~{.sh}
mkdir ~/envprobe
wget http://github.com/whisperity/envprobe/tarball/master -O envprobe.tar.gz
tar xzf envprobe.tar.gz --strip-components=1 -C ~/envprobe/
~~~


### Hook

Envprobe applies the changes to your environment variable every time a prompt is generated in your shell.
For this to work, a hook must be set up in each shell you're using.

The easiest way to do this is to add the hook script at the end of the configuration file for your respective shell.

> **:warning: Note!** If you are using other custom shell extensions, it is **well-advised** for the best experience to load Envprobe **last**.

| Shell                              |             Configuration file (usually)              |                Code to add                |
|:-----------------------------------|:-----------------------------------------------------:|:-----------------------------------------:|
| Bash                               |                   `~/.bashrc`                         | `eval "$(envprobe config hook bash $$)";` |
| Zsh (stock)                        | `~/.zshrc`                                            | `eval "$(envprobe config hook zsh $$)";`  |
| Zsh ([Oh My Zsh](http://ohmyz.sh)) | `~/.oh-my-zsh/custom/zzzzzz_envprobe.zsh` (new file!) | `eval "$(envprobe config hook zsh $$)";`  |


## Quick user guide

If Envprobe is successfully [installed and hooked](#hook), the `ep`/`envprobe` and `epc`/`envprobe-config` convenience _functions_ will be defined in the current shell.
If you see something like below, the tool is good to go.

~~~{.bash}
$ ep
usage: envprobe [-h] ...
~~~

The following guide will show the usage of Envprobe through a few practical examples.

For a complete overview on the commands available and their usage, you can always call `ep -h` (or `ep get -h`, etc. for each subcommand) to get a quick help.
The [complete documentation](http://envprobe.readthedocs.io/en/latest/main/index.html) for the user-facing commands is available behind the link.


### Managing environment variables

For easy access, the environment variable managing commands are also offered as shortcuts.

| Command                 | Shortcut                                            | Usage                          |
|:------------------------|:----------------------------------------------------|:-------------------------------|
| `get VARIABLE`          | `?VARIABLE`, or simply `VARIABLE`                   | Print the value of `VARIABLE`. |
| `set VARIABLE VALUE   ` | `!VARIABLE`, `VARIABLE=VALUE`                       | Sets `VARIABLE` to `VALUE`.    |
| `undefine VARIABLE`     | `^VARIABLE`                                         | Undefine `VARIABLE`.           |
| `add VARIABLE VALUE`    | `+VARIABLE VALUE` (front), `VARIABLE+ VALUE` (back) | Add a `VALUE` to an array.     |
| `remove VARIABLE VALUE` | `-VARIABLE VALUE`                                   | Remove `VALUE` from an array.  |


~~~{.bash}
$ ep get USER
USER=root

$ ep USER
USER=root

$ ep PATH
PATH=/usr/local/bin:/usr/bin:/sbin:/bin

$ echo $SOME_VARIABLE
# No result, variable is not defined.
$ ep SOME_VARIABLE=MyValue
$ echo $SOME_VARIABLE
MyValue

$ ep ^SOME_VARIABLE
$ echo $SOME_VARIABLE
# No result.



$ fancy
fancy: command not found!

$ ep +PATH /opt/fancy/bin
$ fancy
Fancy tool works!

$ ep PATH
PATH=/opt/fancy/bin:/usr/local/bin:/usr/bin:/sbin:/bin

$ pwd
/root

$ ep -PATH /opt/fancy/bin
$ ep PATH+ .
$ ep PATH
PATH=/usr/local/bin:/usr/bin:/sbin:/bin:/root

$ ep +PATH ..
PATH=/:/usr/local/bin:/usr/bin:/sbin:/bin:/root
~~~


### Saved snapshots

For easy access, some of the snapshot management commands are also offered as shortcuts.

| Command                                   | Shortcut                        | Usage                                                                                                                                                           |
|:------------------------------------------|:--------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `diff [var1 var2...]`                     | `% [var1 var2...]`              | Show the difference between the current environment and the last saved one (optionally only for the variables named).                                           |
| `save [--patch] SNAPSHOT [var1 var2...]`  | `}SNAPSHOT [-p] [var1 var2...]` | Save the changes (optionally of only the variables named) to the snapshot named `SNAPSHOT`. If `-p` is given, ask for confirmation of each individual change.   |
| `load [--patch] SNAPSHOT [var1 var2...]`  | `{SNAPSHOT [-p] [var1 var2...]` | Load the changes (optionally to only the variables names) from the snapshot named `SNAPSHOT`. If `-p` is given, ask for confirmation of each individual change. |
| `list`                                    |                                 | List the saved snapshots' names.                                                                                                                                |
| `delete SNAPSHOT`                         |                                 | Delete the snapshot named `SNAPSHOT`.                                                                                                                           |


~~~{.bash}
$ ep %
# (No output, initially the environment hasn't been changed yet.)

$ ep PATH
PATH=/usr/local/bin:/usr/bin/:/sbin:/bin

$ ep SOME_VARIABLE=foo
$ ep +PATH /tmp
$ ep -PATH /sbin
$ ep PATH+ /home/user/bin

$ ep %
(+) Added:       SOME_VARIABLE
        defined value: foo

(!) Changed:     PATH
        added:         /tmp
        added:         /home/user/bin
        removed:       /sbin

$ ep } mypath PATH
For variable 'PATH' the element '/tmp' was added.
For variable 'PATH' the element '/home/user/bin' was added.
For variable 'PATH' the element '/sbin' was removed.

$ ep } other_vars -p
New variable 'SOME_VARIABLE' with value 'foo'.
Save this change? (y/N) _



$ ep list
mypath
other_vars

$ ep delete mypath
$ ep list
other_var



$ ep load custompaths
For variable 'PATH' the element '/srv/custom/bin' will be added.

$ ep PATH
PATH=/srv/custom/bin:/tmp:/home/user/bin

$ ep { foobar -n
New variable 'FOO' will be created with value 'bar'.

$ ep FOO
FOO is not defined

$ ep { foobar -p
New variable 'FOO' will be created with value 'bar'.
Load and apply this change? (y/N) _
~~~

### Saved snapshots

Envprobe offers type safety when accessing environment variables, such as prohibiting assigning a textual value to a `_PID` variable.
The type of a variable is decided based on several heuristics by default, and can be [configured by the user](#configuring-variable-handling).

~~~{.bash}
$ echo $SSH_AGENT_PID
12345

$ export SSH_AGENT_PID="invalid-value"
# The above example works, even though a "_PID" variable should only
# contain numbers.

$ ep SSH_AGENT_PID=98765
$ ep SSH_AGENT_PID="foo"
[ERROR] Failed to execute: could not convert string to number.

$ ep SSH_AGENT_PID
SSH_AGENT_PID=98765
~~~


## Configuring variable handling

The `envprobe-config` (or `epc`) command contains various subcommands that can be used to configure Envprobe's behaviour.

For a complete overview on the commands available and their usage, you can always call `epc -h` (or `epc track -h`, etc. for each subcommand) to get a quick help.
The [complete documentation](http://envprobe.readthedocs.io/en/latest/config/index.html) for the user-facing commands is available behind the link.

|  Command              |  Usage                                                                                                   |
|:----------------------|:---------------------------------------------------------------------------------------------------------|
| `hook ...`            | Generate the [Shell hook](#hook) that allows Envprobe to interface with the environment.                 |
| `set VARIABLE ...`    | Set additional information, such as a *description*, for a variable.                                     |
| `track VARIABLE`      | Configure whether changes to a `VARIABLE` should be managed in [saved snapshots](#saved-snapshots).      |
| `descriptions update` | Download the [variable descriptions](http://github.com/whisperity/Envprobe-Descriptions) to use locally. |


### Obtaining variable type descriptions

Envprobe is managed with a sister project, the *[Envprobe Variable Descriptions Knowledge Base](http://github.com/whisperity/Envprobe-Descriptions)* which contains a curated list of environment variable descriptions and types.
This database is used together with other heuristics to provide type-safe access to variables.
The description of a variable, when queried, may come from a local copy of this database too.
[Read more about this feature.](http://envprobe.readthedocs.io/en/latest/community_descriptions.html)

To initially download, or subsequently update, the description database, execute:

    epc descriptions update
