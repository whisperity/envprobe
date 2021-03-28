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
- [Configuring variable handling](#configuring-variable-handling)

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

You can grab Envprobe from the GitHub repository, either via `git` or in a tarball form.
Download the project anywhere you please.
In this example, we'll use `~/envprobe`.

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

| Shell                              |             Configuration file (usually)              |                     Code to add                      |
|:-----------------------------------|:-----------------------------------------------------:|:----------------------------------------------------:|
| Bash                               |                   `~/.bashrc`                         | `eval "$(~/envprobe/envprobe config hook bash $$)";` |
| Zsh (stock)                        | `~/.zshrc`                                            | `eval "$(~/envprobe/envprobe config hook zsh $$)";`  |
| Zsh ([Oh My Zsh](http://ohmyz.sh)) | `~/.oh-my-zsh/custom/zzzzzz_envprobe.zsh` (new file!) | `eval "$(~/envprobe/envprobe config hook zsh $$)";`  |


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


## Configuring variable handling

The `envprobe-config` (or `epc`) command contains various subcommands that can be used to configure Envprobe's behaviour.


For a complete overview on the commands available and their usage, you can always call `epc -h` (or `epc track -h`, etc. for each subcommand) to get a quick help.
The [complete documentation](http://envprobe.readthedocs.io/en/latest/config/index.html) for the user-facing commands is available behind the link.

|  Command   |  Usage                                                                                                       |
|:-----------|:-------------------------------------------------------------------------------------------------------------|
| `hook ...`          | Generate the [Shell hook](#hook) that allows Envprobe to interface with the environment.            |
| `track VARIABLE`    | Configure whether changes to a `VARIABLE` should be managed in [saved snapshots](#saved-snapshots). |


---

---

# :warning: OLD DOCUMENTATION

> :loudspeaker: Below follows the documentation for the **previous version** of Envprobe that is being rewritten.
> Some of the parts might no longer or not yet apply!

Why?
----

Currently for developers to set up their environments, a lot of configuration
files, aliases and the like need to be set up. Conventionally, you can use
bare `export`-like commands for that. Sometimes, `direnv` can do the job, if
your configuration has to apply to a certain subtree in the filesystem. When
you need things loaded into your shell, Modules is &ndash; at least
allegedly &ndash; the way to go. Alternatively, one can use
[Docker](http://docker.com/) to run environments within containers.

However, there is a use case on which all of the aforementioned tools fall
short, or are hard to configure. **`envprobe`** &mdash; the name idea came
from [`modprobe`](http://enwp.org/Modprobe), but for environments &mdash;
was born out of this personal necessity, to give the ability to easily
configure your shell, without the need of actually writing tedious
configuration files, to either of these mentioned systems.



How to Install?
---------------


### Invoking *Envprobe*

After envprobe is installed, you can use it in the shell with the `envprobe`
or `ep` command. **You should NOT alter `PATH` or use the absolute
`~/envprobe/envprobe.py` path to access `envprobe`.** The hook executed by
the lines above enabled `envprobe` for you.



Advanced: Configuring type of variables
---------------------------------------

Conventionally shells store every environment variable as a string, and only
when needed try to interpret them as numbers, arrays, etc. However, to provide
a marginally safer experience, Envprobe defines its own types and uses them
when the user accesses a variable.

These types are as follows. (Please see the help at `epc set-type --help` for
the list of types that are loaded into the current running Envprobe instance.)

 * `string`: This is the basic type, the variable is represented as a string.
 * `number`: Either integer or floating-point numbers.
 * `colon-separated` and `semi-separated`: Array of strings, separated by `:`
   or `;`.
 * `path`: A special `:`-separated array which contains files or folder
   directives.
 * `ignored`: Remove the variable from Envprobe's allowed and managed
   variables.

*Note:* Setting a variable's *type* to `ignored` is not the same as
*"tracking ignoring"* a variable. "Tracking ignore" means that changes of the
variable is not visible to the `diff`, `save`, `load`, ... commands, but
the variable can still be managed locally, in an ad-hoc fashion. A variable
with `ignored` type will result in Envprobe rejecting every access (`get`,
`set`) on that variable.

Envprobe contains built-in heuristics to figure out the type of a variable, but
in case you know your environment better, you can specify Envprobe not to stand
in your way, with the `epc set-type` command:

    epc set-type MY_VARIABLE -t path

The above example sets the type &mdash; this is your user's configuration
saved locally &mdash; of `MY_VARIABLE` to `path`. In your shells, your
configuration overrides the built-in heuristics, and the variable will always
be considered what you specified.

To delete a preference, use `-d`: `epc set-type MY_VARIABLE -d`. This will
revert `MY_VARIABLE` back to the default heuristic.



Advanced: Describing variables
------------------------------

Apart from specifying their type, you can also specify a *description* to
save what a variable describes.

    epc set-description MY_VARIABLE "Very fancy variable"

The description for a variable can be retrieved by specifying `--info` for
the `get` command:

    $ ep get MY_VARIABLE --info
    MY_VARIABLE=fancy

    Type: 'string'
    Description:
      Very fancy variable
    Source: local



Advanced: Obtaining variable types and descriptions from the community
----------------------------------------------------------------------

> **Note:** This is the **only** part in Envprobe which communicates with
> a remote server. No personal data is transmitted &mdash; at least directly
> by Envprobe &mdash;. The network transaction only downloads a single file
> *from GitHub* to fetch the knowledge-base.

A sister project for *Envprobe* exists, with the title
[*Envprobe: Descriptions*](http://github.com/whisperity/envprobe-descriptions)
. This project is aimed at collecting knowledge about environment variables,
which includes their proper type and description, usage.

Envprobe supports automatically fetching the knowledge base and store it for
your user. This database is used to get *type* and *description* metadata
for environment variables &mdash; unless you locally override these details.

To update the download of the description database, execute:

    epc update-community

*Note:* Depending on the size of the knowledgebase and the available Internet
connection, the download could take up some time, and also use data. To
conserve your resources, we advise *NOT* to update on metered connections!


Extreme: Resetting or hacking *Envprobe*
----------------------------------------

We share the philosophy of small individual commands and easily readable
configuration files in this project. Your local configuration is saved under
`~/.local/share/envprobe` in the form of JSON files. Adventurous and power
users are welcome to tinker their configuration through these files, but be
advised that we cannot provide any help in case a mess-up happens.

To make Envprobe *completely **and irrevocably** forget* all configuration,
along with **all your saved states!**, simply delete the aforementioned folder,
and then restart your Terminal.

**Warning!** Data and configuration specific to a running shell session is
saved to a temporary folder and might include binary files and files with
ephemeral lifespan. These files are not meant to be altered manually apart
from development or debugging purposes. Altering these files can make your
running shell irrevocably broken!
