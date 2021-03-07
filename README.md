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

If Envprobe is successfully [installed and hooked](#installation.hook), the `ep`/`envprobe` and `epc`/`envprobe-config` convenience _functions_ will be defined in the current shell.
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

| Command                 | Shortcut                                            | Usage                         |
|:------------------------|:----------------------------------------------------|:------------------------------|
| `get VARIABLE`          | `?VARIABLE` or simply `VARIABLE`                    | Print the value of `VARIABLE` |
| `set VARIABLE VALUE   ` | `!VARIABLE`, `VARIABLE=VALUE`                       | Sets `VARIABLE` to `VALUE`    |
| `undefine VARIABLE`     | `^VARIABLE`                                         | Undefine `VARIABLE`           |
| `add VARIABLE VALUE`    | `+VARIABLE VALUE` (front), `VARIABLE+ VALUE` (back) | Add a `VALUE` to an array     |
| `remove VARIABLE VALUE` | `-VARIABLE VALUE`                                   | Remove `VALUE` from an array  |


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

| Command                 | Shortcut                                            | Usage                         |
|:------------------------|:----------------------------------------------------|:----------------------------------------------------------------------------|
| `diff`                  | `%`                                                 | Show the difference between the current environment and the last saved one. |


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
~~~

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



Overview example
----------------

In one shell:

```bash
$ ep save fancy
```

Then, in another shell:

```bash
$ ep +PATH /some/unrelated/tool
$ unrelated-tool
Unrelated: works!

$ ep load fancy
$ fancy
Fancy tool works! --too!--

$ ep PATH
PATH=/opt/fancy/bin:/some/unrelated/tool:/bin
```

Usage: Saving and loading environments
--------------------------------------

In this section, the tools for managing variable changes between shells is
explained. This is *the core* feature of Envprobe, allowing you to quickly
save environment changes and re-use them later, without the need of manually
writing shell scripts, configuration files.

(Shortcuts for the long form of actions is presented between `{` and `}`
on the right side.)

~~~
list                List the names of saved differences.
load                {{NAME} Load differences from a named save and apply them.
save                {}NAME} Save changes in the environment into a named save.
delete              Delete a named save.
~~~


### Saving and loading differences

The `save` and `load` commands (shortcut letters: `}` and `{`) are used to
write the difference of environment variables to a persisted "state save file",
and to apply such states onto the current shell.

Each saved state has a distinct *name*. These saved differences are only
available to your user on the computer, but are shared between shells, and
kept between reboots.

To save the current difference to `my_env`, execute

    ep save my_env

To update the current shell's variables based on what difference was written
to `my_env`, use

    ep load my_env

Both commands take an optional *list of variable names* (if given, only the
variables in this list will be saved or loaded), and a toggle for *`--patch`
mode*. In *patch mode*, each individual change has to be confirmed first on
the Terminal.

~~~
$ ep save -p fancy
Variable "FANCY_VARIABLE" set to value: 'very-fancy'.
Save this change? (y/N) _
~~~


#### Updating saves

In case the same *name* is used in multiple `save` commands, only changes to
the same variable overwrite previous instances. The save file is automatically
updated and appended with the new values. To completely overwrite a save,
it must be deleted first.


#### Inspecting a saved difference (`load --dry-run`)

To see what variable changes would take effect if a saved state was applied,
specify `--dry-run`.

~~~
In variable "PATH", the value (component) '/opt/fancy/bin' will be added.
In variable "PATH", the value (component) '/usr/bin' will be removed.
New variable "FANCY_VARIABLE" will be set to value: 'very-fancy'.
Variable "VISUAL" will be unset (from value: 'vim')
~~~

> *Note:* In traditional differences and version control systems, the
> difference is a change from a previous value to a new one. To aid easier
> management of environment, the "previous value" side is only emitted for
> the user's clarity &mdash; it is **NOT** taken into account when saving
> and applying a difference.
>
> In the above example, `VISUAL` will be unset when the saved difference is
> applied even if its value is not `vim`, although at the time of saving
> the difference, it was.


### Listing and deleting differences

The list of saved differences available to your user can be listed with
`ep list`:

    $ ep list
    - fancy
    - my_env

A saved difference can be deleted with the `delete` command:

    ep delete my_env



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


Advanced: Tracking and ignoring variables
-----------------------------------------

By default, Envprobe tracks the change to every variable (except a very few
very special ones which are deliberately hidden!). There might be a case this
is not the expected behaviour for a workflow. In this case, the `epc track`
command can be used to fine-tune which variables should be tracked and ignored.

    epc track VARIABLE         # Will set VARIABLE to be tracked.
    epc track -i VARIABLE      # Will set VARIABLE to be ignored.

If a variable is *tracked*, changes to this variable will be shown in `diff`,
can be `save`d and `load`ed. If a variable is *ignored*, no change related to
it is managed by Envprobe, and in case a saved state's `load` wants to change
such a variable, it will be left without change.

~~~
$ epc track --ignore PATH
$ ep +PATH /foo
$ ep diff
(empty)
~~~

If the `--global` option is specified, the change in the tracking of a variable
will be saved for your entire user, not just the current shell.

If a variable is not explicitly *tracked* nor *ignored*, the default tracking
dictates what will happen. This default can be changed with the
`epc default-tracking` command.

    epc default-tracking --disable

~~~
$ epc track MY_VAR
$ ep MY_VAR="foo"
$ ep diff
+ Added:    MY_VAR
     value: foo
~~~


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
