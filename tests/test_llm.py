"""LLM hook smoke tests: rule fallback must be deterministic and equivalent."""
from wolfbench.agents.llm import (
    RuleFallbackBackend, LLMPumpLeader, LLMFinfluencer, LLMRuleAssistWolfGuardAgent,
    LLMWolfGuardAgent,
    VLLMChatBackend, _loads_json_dict,
)
from wolfbench.agents.wolfguard import WolfGuardConfig
from wolfbench.defense import get_policy, get_track
from wolfbench.env.environment import WolfBenchEnv
from wolfbench.scenarios.base import load_scenario


def test_llm_pump_leader_with_rule_fallback_matches_rule():
    """With RuleFallbackBackend, LLMPumpLeader must yield identical episode."""
    scen = load_scenario("s1")
    a = WolfBenchEnv(scen, n_society=300, alpha=0.05, seed=7).run()
    b = WolfBenchEnv(scen, n_society=300, alpha=0.05, seed=7,
                     llm_backend=RuleFallbackBackend(), n_llm_leaders=4).run()
    assert a.metrics.max_collapse_score == b.metrics.max_collapse_score
    assert a.metrics.collapse_day == b.metrics.collapse_day


def test_llm_leader_count_capped():
    scen = load_scenario("s1")
    # request many LLM leaders; sublinear schedule caps at 10 globally
    env = WolfBenchEnv(scen, n_society=100000, alpha=0.20, seed=1,
                       llm_backend=RuleFallbackBackend(),
                       n_llm_leaders=1000)
    n_llm = sum(isinstance(a, LLMPumpLeader) for a in env.society.attackers)
    assert n_llm <= 10, f"LLM leaders not capped: got {n_llm}"


def test_llm_finfluencer_capped_independent_of_alpha():
    scen = load_scenario("s2")
    for alpha in [0.01, 0.05, 0.20]:
        env = WolfBenchEnv(scen, n_society=5000, alpha=alpha, seed=1,
                           llm_backend=RuleFallbackBackend(),
                           n_llm_leaders=100)
        n_llm = sum(isinstance(a, LLMFinfluencer) for a in env.society.attackers)
        assert n_llm <= 5, f"alpha={alpha}: LLM finfluencers={n_llm}"


def test_llm_count_sublinear_schedule():
    """Verify the (N, alpha) → K_LLM table from paper §LLM-scaling."""
    from wolfbench.scenarios.society import strategic_leader_count
    expected = {
        (100, 0.01): 1, (100, 0.05): 2, (100, 0.10): 2,
        (1000, 0.01): 2, (1000, 0.05): 3, (1000, 0.10): 3,
        (10000, 0.005): 2, (10000, 0.01): 3, (10000, 0.05): 5,
        (100000, 0.01): 6, (100000, 0.05): 10, (100000, 0.10): 10,
    }
    for (N, a), k in expected.items():
        n_h = max(1, int(round(a * N)))
        got = strategic_leader_count(N, a, n_h)
        assert got == k, f"N={N} alpha={a}: expected {k}, got {got}"


def test_vllm_backend_is_lazy_and_strict_by_default():
    backend = VLLMChatBackend(model="qwen3-8b", base_url="http://127.0.0.1:9/v1")
    assert backend.name == "vllm_chat"
    assert backend.strict is True
    assert backend.calls == 0


def test_qwen_policy_factory_uses_vllm_without_calling_server():
    policy = get_policy("qwen", model="qwen3-8b",
                        base_url="http://127.0.0.1:9/v1")
    assert "Qwen3-vLLM" in policy.name
    assert policy.backend.name == "vllm_chat"
    assert policy.backend.calls == 0


def test_qwen_assisted_policy_factory_is_separate_track():
    policy = get_policy("qwen_assisted", model="qwen3-8b",
                        base_url="http://127.0.0.1:9/v1")
    assert isinstance(policy, LLMRuleAssistWolfGuardAgent)
    assert get_track("qwen_assisted") == "llm_assisted_rule"
    assert get_track("qwen") == "llm_from_scratch"


def test_llm_json_parser_strips_qwen_thinking_and_fences():
    content = '<think>draft</think>\n```json\n{"asset_2": {"action": "warning"}}\n```'
    assert _loads_json_dict(content) == {"asset_2": {"action": "warning"}}


class CaptureBackend:
    name = "capture"

    def __init__(self, response=None):
        self.user = ""
        self.response = response or {}

    def chat_json(self, system, user):
        self.user = user
        return self.response


def test_llm_wolfguard_does_not_prompt_with_oracle_view():
    backend = CaptureBackend()
    agent = LLMWolfGuardAgent(backend=backend, config=WolfGuardConfig())
    summary = {
        "day": 1,
        "market": {"asset_2": {"price": 4.0, "fundamental": 4.0}},
        "social": {"asset_2": {}},
        "recent_return": {"asset_2": 0.0},
        "oracle_view": {"asset_2": {"harmful_pressure": 1.0}},
    }
    agent.decide(1, summary)
    assert "oracle_view" not in backend.user
    assert '"actions"' not in backend.user


def test_llm_wolfguard_can_act_without_rule_action_seed():
    backend = CaptureBackend({"asset_2": {"action": "warning", "risk": 0.6}})
    agent = LLMWolfGuardAgent(backend=backend, config=WolfGuardConfig())
    summary = {
        "day": 1,
        "market": {"asset_2": {"price": 4.0, "fundamental": 4.0}},
        "social": {"asset_2": {}},
        "recent_return": {"asset_2": 0.0},
        "oracle_view": {},
    }
    actions = agent.decide(1, summary)
    assert actions["asset_2"]["action"] == "warning"
    assert actions["asset_2"]["risk"] == 0.6
