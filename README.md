envprobe
========

> Overlaying pluggable environment setter:
> [modules](http://modules.sourceforge.net/) reimagined + toggleable
> [`direnv`](http://direnv.net/) on the shell, rather than the directory
> level.

**Envprobe** (or `envprobe`, after the command entry point) is a shell
configuration tool written in Python.



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


### Dependencies

Currently, the main target supported by *`envprobe`* is Ubuntu 16.04 LTS,
using the Bash-like shells, namely Bash and Zsh.

You'll need Python 3 installed on your system. The version available in the
package manager should be good enough.


### Obtaining *Envprobe*

Check out the official repository of `envprobe` to an arbitrary folder on
your system. For convenience, we'll use `~/envprobe` as location:

    git clone http://github.com/whisperity/envprobe.git ~/envprobe \
      --origin upstream \
      --single-branch --branch master \
      --depth 1


### Installation


#### Bash

Add the following lines to your `~/.bashrc` file, generally at the very end
of it. These lines help hooking `envprobe` into your running shells.

```bash
unset  ENVPROBE_CONFIG
export ENVPROBE_LOCATION=~/envprobe
export ENVPROBE_SHELL_PID=$$
eval   "$(${ENVPROBE_LOCATION}/envprobe-config.py shell bash)"
alias  ep='envprobe'
alias  epc='envprobe-config'
```

#### Zsh

Add the following lines to your `~/.zshrc` file, generally at the very end
of it. These lines help hooking `envprobe` into your running shells.

```zsh
unset  ENVPROBE_CONFIG
export ENVPROBE_LOCATION=~/envprobe
export ENVPROBE_SHELL_PID=$$
eval   "$(${ENVPROBE_LOCATION}/envprobe-config.py shell zsh)"
alias  ep='envprobe'
alias  epc='envprobe-config'
```

#### Other extensions

If you are using any other extensions in your shell (such as `byobu-shell` or
[Bash Git Prompt](https://github.com/magicmonty/bash-git-prompt)), the added
lines need to be after the configuration of your existing extensions.


### Invoking *Envprobe*

After envprobe is installed, you can use it in the shell with the `envprobe`
or `ep` command. **You should NOT alter `PATH` or use the absolute
`~/envprobe/envprobe.py` path to access `envprobe`.** The hook executed by
the lines above enabled `envprobe` for you.



Overview example
----------------

In one shell:

```bash
$ ep PATH
PATH=/bin

$ fancy
Error! fancy: command not found

$ ep +PATH /opt/fancy/bin
$ ep PATH
PATH=/opt/fancy/bin:/bin

$ fancy
Fancy tool works!

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

Usage: Accessing current environment variables
----------------------------------------------

Envprobe offers an easy interface that helps you manage environment variables
of the current shell.

(Shortcuts for the long form of actions is presented between `{` and `}`
on the right side.)

~~~
get                 {?VARIABLE} Print the value of an environmental
                    variable.
set                 {VARIABLE=VALUE} Set the environmental variable to a
                    given value.
add                 {+VARIABLE VALUE} Add values to an array-like
                    environmental variable.
remove              {-VARIABLE VALUE} Remove values from an array-like
                    environmental variable.
undefine            {^VARIABLE} Undefine an environmental variable.
~~~


### Querying and changing

The `get` and `set` actions can be used to print or change the value of a
variable.

To query your `EDITOR`:

    ep get EDITOR

To set `EDITOR` to something else:

    ep set EDITOR your-favourite-editor

The shortcut characters `?` and `=` can be used instead of `get` and `set`
like this:

    ep ?EDITOR
    ep EDITOR=your-favourite-editor

Alternatively, for ease of access on *checking* a variable in the current
shell, there is no need to type `?` in either:

    ep PATH

> This syntax is 37.5% shorter than the in-all-case equivalent `echo ${PATH}`.

(The special character can appear either as the first and as the last letter
of the command. If you are fancy of Haskell and prefix syntax, you can say
something like the following. The "prefix" and "suffix" forms are equivalent.)

    ep =EDITOR your-favourite-editor
    ep = EDITOR your-favourite-editor
    ep EDITOR?
    ep EDITOR ?


### Adding and removing "array-like" components (e.g. `PATH`)

Traditionally, extending `PATH` with your current working directory required
a lengthy sequence: `export PATH="$(pwd):${PATH}"`. Envprobe provides support
for "array-like" environment variables via the `add` and `remove` commands,
which insert or remove an element from an array.

Currently, variables whose name include the substring `PATH` are considered
as array variables. (This is expected to change to be more configurable as
`envprobe`'s development furthers.)

To remove `/usr/bin` from your `PATH`, type either the long or the short form:

    ep remove PATH /usr/bin
    ep -PATH /usr/bin

To add your current directory to `CMAKE_PREFIX_PATH`:

    ep add CMAKE_PREFIX_PATH `pwd`
    ep +CMAKE_PREFIX_PATH `pwd`

#### Adding values at a certain position

`add` also supports suffixing the array with the argument, i.e. adding it as
the last element. **Note, that *unlike `?VAR` and `VAR?`*, `+VAR` and `VAR+`
are *NOT* equivalent commands.**

    ep add --position -1 CMAKE_PREFIX_PATH `pwd`
    ep CMAKE_PREFIX_PATH+ `pwd`

You can insert the command-line argument to anywhere in the array with giving
a `--position`.

#### Adding and removing multiple values

`add` and `remove` take multiple values, which will be added to or removed
from the environment variable. In case of `add`, if a position (e.g.
`--position 1` or `+VARIABLE` is used), the arguments are added in the order
they are specified:

    $ echo ${PATH}
    > /usr/bin

    $ ep +PATH /one /two   # Or: ep add --position 1 PATH /one /two
    $ echo ${PATH}
    > /one:/two:/usr/bin

Directly overwriting an array-like variable is supported too. In this case,
the value given to `set` must be the proper string form of the array, just
like how traditionally one would give it to `export`.

    ep set PATH /home/username:/usr/bin
    ep PATH=/home/username:/usr/bin

#### Undefining a variable

To make a variable undefined, use the `undefine` (`^`) command:

    ep undefine BUILD_ID
    ep ^BUILD_ID



Usage: Saving and loading environments
-------------------------------------------

In this section, the tools for managing variable changes between shells is
explained. This is *the core* feature of Envprobe, allowing you to quickly
save environment changes and re-use them later, without the need of manually
writing shell scripts, configuration files.

(Shortcuts for the long form of actions is presented between `{` and `}`
on the right side.)

~~~
list                List the names of saved differences.
load                {{NAME} Load differences from a named save and apply them.
diff                {%} Show difference of shell vs. previous save/load.
save                {}NAME} Save changes in the environment into a named save.
delete              Delete a named save.
~~~


### Showing the difference

The change of variables are recorded(*) relative to the initial state of the
shell. This record is updated when changes are saved or loaded (more about
it later).

To view the changes of variables in the current shell, say `ep %` (in long
form, `envprobe diff`):

~~~
+ Added:    FANCY_VARIABLE
     value: very-fancy

! Modified: PATH
      added /opt/fancy/bin
    removed /usr/sbin

- Removed:  VISUAL
     value: vim
~~~

> **(\*):** `recorded` in this context means a difference ledger kept **entirely
> on the local machine**. *Envprobe* does not transmit/store your
> configuration to/on any remote system.


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
