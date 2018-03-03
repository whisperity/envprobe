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
export ENVPROBE_LOCATION="~/envprobe";
export ENVPROBE_SHELL_PID=$$;
eval "$(${ENVPROBE_LOCATION}/envprobe.py shell bash)"
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
