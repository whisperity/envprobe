import pytest

from envprobe.environment import EnvVarTypeHeuristic, HeuristicStack, \
        create_environment_variable


def test_default():
    h = EnvVarTypeHeuristic()
    assert(h(None) == "string")
    assert(h("") == "string")
    assert(h("foo") == "string")


class EmptyHeuristic(EnvVarTypeHeuristic):
    def __call__(self, name, env=None):
        return None


class TestHeuristic(EnvVarTypeHeuristic):
    def __call__(self, name, env=None):
        if name == "test":
            return "test"
        if name == "break":
            return False
        return None


def test_pipeline():
    p = HeuristicStack()
    assert(p("Variable") is None)

    p += EmptyHeuristic()
    assert(p("Variable") is None)

    p += EnvVarTypeHeuristic()
    assert(p("Variable") == "string")

    p += TestHeuristic()
    assert(p("Variable") == "string")
    assert(p("test") == "test")

    p += EmptyHeuristic()
    assert(p("Variable") == "string")
    assert(p("test") == "test")

    assert(p("break") is None)


def test_pipeline_simple():
    p = HeuristicStack()
    p += EnvVarTypeHeuristic()
    p += TestHeuristic()
    assert(p("Variable") == "string")
    assert(p("test") == "test")


class NumericHeuristic():
    def __call__(self, name, env=None):
        if name not in env:
            return None

        try:
            float(env[name])
            return "numeric"
        except ValueError:
            return None


def test_creation():
    p = HeuristicStack()
    p += EnvVarTypeHeuristic()
    p += NumericHeuristic()

    env = {"variable": 5}

    num_var = create_environment_variable("variable", env, p)
    assert(num_var)
    assert(num_var.value == 5)


def test_ignore():
    p = HeuristicStack()
    p += EnvVarTypeHeuristic()
    p += TestHeuristic()

    env = {"variable": "X", "break": None}

    var = create_environment_variable("variable", env, p)
    assert(var)
    assert(var.value == env["variable"])

    with pytest.raises(KeyError):
        breakvar = create_environment_variable("break", env, p)
