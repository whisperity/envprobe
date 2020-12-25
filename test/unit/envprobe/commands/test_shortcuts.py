# Note that these tests do not concern whether the rewritten shortcut, such as
# "ep undefine FOO bar" is a legit call or not, only testing the rewriting
# logic from the symbol shortcut to the full command.
import shlex

from envprobe.commands.shortcuts import transform_subcommand_shortcut


def target(arg_string):
    args_to_pass = ["envprobe"] + shlex.split(arg_string)
    result = transform_subcommand_shortcut(args_to_pass, ["__RESERVED"])
    assert(result[0] == "envprobe")
    return result[1:]


def test_basic():
    assert(target("") == [])
    assert(target("-h") == ["-h"])
    assert(target("--help") == ["--help"])


def test_add():
    assert(target("+") == ["add"])
    assert(target("+ PATH") == ["add", "PATH"])
    assert(target("+ PATH foo") == ["add", "PATH", "foo"])
    assert(target("+PATH foo") == ["add", "PATH", "foo"])

    assert(target("+ PATH foo bar") == ["add", "PATH", "foo", "bar"])
    assert(target("+PATH foo bar") == ["add", "PATH", "foo", "bar"])

    assert(target("PATH +") == ["add", "--position", "-1", "PATH"])
    assert(target("PATH + foo") == ["add", "--position", "-1", "PATH", "foo"])
    assert(target("PATH+ foo") == ["add", "--position", "-1", "PATH", "foo"])

    assert(target("PATH + foo bar") ==
           ["add", "--position", "-1", "PATH", "foo", "bar"])
    assert(target("PATH+ foo bar") ==
           ["add", "--position", "-1", "PATH", "foo", "bar"])


def test_remove():
    assert(target("-") == ["remove"])
    assert(target("- PATH") == ["remove", "PATH"])
    assert(target("- PATH foo") == ["remove", "PATH", "foo"])
    assert(target("-PATH foo") == ["remove", "PATH", "foo"])

    assert(target("- PATH foo bar") == ["remove", "PATH", "foo", "bar"])
    assert(target("-PATH foo bar") == ["remove", "PATH", "foo", "bar"])


def test_get():
    assert(target("?") == ["get"])
    assert(target("? PATH") == ["get", "PATH"])
    assert(target("? PATH foo") == ["get", "PATH", "foo"])
    assert(target("?PATH foo") == ["get", "PATH", "foo"])

    assert(target("PATH") == ["get", "PATH"])


def test_get_on_varname_colliding_with_reserved_command():
    # Note that subcommands that are considered registered valid commands
    # should NOT be rewritten to a "get" call.
    assert(target("__RESERVED") != ["get", "__RESERVED"])
    assert(target("__RESERVED") == ["__RESERVED"])


def test_set():
    assert(target("!") == ["set"])
    assert(target("! PATH") == ["set", "PATH"])
    assert(target("! PATH foo") == ["set", "PATH", "foo"])
    assert(target("!PATH foo") == ["set", "PATH", "foo"])

    assert(target("=") == ["set"])
    assert(target("= PATH") == ["set", "PATH"])
    assert(target("= PATH foo") == ["set", "PATH", "foo"])
    assert(target("=PATH foo") == ["set", "PATH", "foo"])

    assert(target("=") == ["set"])
    assert(target("PATH=") == ["set", "PATH"])
    assert(target("PATH = foo") == ["set", "PATH", "foo"])
    assert(target("PATH=foo") == ["set", "PATH", "foo"])

    assert(target("PATH=\"\"") == ["set", "PATH"])


def test_undefine():
    assert(target("^") == ["undefine"])
    assert(target("^ PATH") == ["undefine", "PATH"])
    assert(target("^ PATH foo") == ["undefine", "PATH", "foo"])
    assert(target("^PATH foo") == ["undefine", "PATH", "foo"])


def test_load():
    assert(target("{") == ["load"])
    assert(target("{ PATH") == ["load", "PATH"])
    assert(target("{ PATH foo") == ["load", "PATH", "foo"])
    assert(target("{PATH foo") == ["load", "PATH", "foo"])


def test_save():
    assert(target("}") == ["save"])
    assert(target("} PATH") == ["save", "PATH"])
    assert(target("} PATH foo") == ["save", "PATH", "foo"])
    assert(target("}PATH foo") == ["save", "PATH", "foo"])


def test_diff():
    assert(target("%") == ["diff"])
    assert(target("% PATH") == ["diff", "PATH"])
    assert(target("% PATH foo") == ["diff", "PATH", "foo"])
    assert(target("%PATH foo") == ["diff", "PATH", "foo"])
