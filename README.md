envprobe
========

(Overlaying &mdash; Will be!) environment setter. Basically
[Modules](http://modules.sourceforge.net/) re-imagined and joined with the
awesomeness of [`direnv`](http://direnv.net/), but on the shell level.

Why?
----

Currently for developers to set up their environments, a lot of configuration
files, aliases and the like needs to be set up. Conventionally, you can use
bare `export` commands for that. Sometimes, `direnv` can do the job, if your
configuration has to apply to a certain subtree. When you need things loaded
into your shell, Modules is &ndash; at least allegedly &ndash; the way to go.
Alternatively, one can use [Docker](http://docker.com/) to run environments
within containers.

However, there is a use case on which all of the aforementioned tools fall
short, or are hard to configure. **`envprobe`** &ndash; the name idea came
from `modprobe`, but for environments &ndash; was born out of this personal
necessity, to give the ability to easily configure your shell, without the need
of actually writing tedious configuration files.

How to Install?
---------------

Currently, the main target supported by `envprobe` is Ubuntu 16.04 LTS, using
the Bash shell.

You'll need Python 3 installed on your system.

Check out the official repository of `envprobe` to an arbitrary folder on
your system. For convenience, we'll use `~/envprobe` as location:

    git clone http://github.com/whisperity/envprobe.git ~/envprobe \
      --origin upstream \
      --single-branch --branch master \
      --depth 1

Add the following lines to your `~/.bashrc` file, generally at the very end
of it. These lines are necessary to ensure that `envprobe` is available and
can see your active shells.

```bash
export ENVPROBE_LOCATION=~/envprobe;
export ENVPROBE_SHELL_PID=$$;
eval "$(${ENVPROBE_LOCATION}/envprobe.py shell bash)";
alias ep='envprobe';
```

If you are using any other extensions in your shell (such as `byobu-shell` or
[Bash Git Prompt](https://github.com/magicmonty/bash-git-prompt)), the added
lines need to be after the configuration of your existing extensions.

Make sure to reload your configuration by executing `source ~/.bashrc`, or by
simply restarting your shell.

After envprobe is installed, you can use it in the shell with the `envprobe`
command. **You should NOT alter `PATH` or use the absolute
`~/envprobe/envprobe.py` path to access `envprobe`.** The hook executed by
the lines above should take care of enabling `envprobe` for you.

Usage for environment variables
-------------------------------

### Querying and setting environment variables

Envprobe uses the actions `get` and `set` to access environment variables.
After a variable is set, your shell will load its value at the next prompt
print.

To query your `EDITOR`:

    ep get EDITOR

To set `EDITOR` to something else:

    ep set EDITOR your-favourite-editor

The shortcut characters `?` and `=` can be used instead of `get` and `set`
like this:

    ep ?EDITOR
    ep EDITOR=your-favourite-editor

The special character can appear either as the first and as the last letter
of the command. If you are fancy of Haskell and prefix syntax, you can say
something like this below. The "prefix" and "suffix" forms are equivalent.

    ep =EDITOR your-favourite-editor
    ep = EDITOR your-favourite-editor
    ep EDITOR?
    ep EDITOR ?

### Extending and removing from "array-like" environment variables (e.g. `PATH`)

Traditionally, extending `PATH` with your current working directory required
a lengthy sequence: `export PATH="$(pwd):${PATH}"`. Envprobe provides support
for "array-like" environment variables via the `add` and `remove` command,
which insert or remove an element from the array. The environment variable is
automatically reformatted to include all the elements that were not modified.

Currently, variables whose name include the substring `PATH` are considered
as array variables. (This is expected to change to be more configurable as
`envprobe`'s development furthers.)

To remove `/usr/bin` from your `PATH`, say either the long or the short form:

    ep remove PATH /usr/bin
    ep -PATH /usr/bin

To add your current directory to `CMAKE_PREFIX_PATH`:

    ep add CMAKE_PREFIX_PATH `pwd`
    ep +CMAKE_PREFIX_PATH `pwd`

#### Adding values at a certain position

`add` also supports suffixing the array with the argument, i.e. adding it as
the last element. **Be careful, `+VAR` and `VAR+` are *NOT* equivalent
commands.**

    ep add --position -1 CMAKE_PREFIX_PATH `pwd`
    ep CMAKE_PREFIX_PATH+ `pwd`

You can insert the command-line argument to anywhere in the array with giving
a `--position`.

#### Adding and removing multiple values

`add` and `remove` take multiple values, which will be added to or removed
from the environment variable. In case of `add`, if a position (e.g.
`--position 1` or `+VARIABLE` is used), the arguments are added in the order
they are specified:

    $ echo $PATH
    > /usr/bin

    $ ep +PATH /one /two   # Or: ep add --position 1 PATH /one /two
    $ echo $PATH
    > /one:/two:/usr/bin

Of course, directly overwriting an environment variable is also supported. In
this case, the value given to `set` must be the proper string of the array:

    ep set PATH /home/username:/usr/bin
    ep PATH=/home/username:/usr/bin

Usage for saving environment configurations
-------------------------------------------

> Coming soon...
