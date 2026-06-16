from wolfbench.data import episode_to_trajectory_records
from wolfbench.defense import get_track
from wolfbench.defense.distilled import DistilledWolfGuardPolicy, train_distilled_model
from wolfbench.env.environment import WolfBenchEnv
from wolfbench.scenarios.base import load_scenario


def test_trajectory_records_hide_oracle_from_public_observation():
    scen = load_scenario("s1")
    res = WolfBenchEnv(scen, n_society=120, alpha=0.05, seed=3,
                       record_trajectory=True).run()

    records = episode_to_trajectory_records(res, split="public_dev")
    assert records
    assert all("oracle_view" not in r["observation"] for r in records)
    assert all(r["label_available"] for r in records)
    assert {r["oracle_label"] for r in records}.issubset(
        {"none", "warning", "cooldown", "block"}
    )

    heldout = episode_to_trajectory_records(res, split="public_test")
    assert heldout
    assert all(not r["label_available"] for r in heldout)
    assert all(r["oracle_label"] is None for r in heldout)
    assert all(r["future_collapse"] is None for r in heldout)


def test_distilled_wolfguard_trains_loads_and_decides(tmp_path):
    scen = load_scenario("s1")
    res = WolfBenchEnv(scen, n_society=120, alpha=0.05, seed=4,
                       record_trajectory=True).run()
    records = episode_to_trajectory_records(res, split="public_dev")

    model = train_distilled_model(records, epochs=5, lr=0.05, seed=7)
    model_path = tmp_path / "distilled.json"
    model.save(model_path)

    policy = DistilledWolfGuardPolicy(model_path=str(model_path))
    summary = records[0]["observation"]
    actions = policy.decide(day=records[0]["day"], summary=summary)

    assert get_track("distilled") == "simulator_trained_baseline"
    assert set(actions) == set(summary["market"])
    assert all(a["action"] in {"none", "warning", "cooldown", "block"}
               for a in actions.values())