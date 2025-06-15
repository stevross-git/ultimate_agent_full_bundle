from ultimate_agent.blockchain.incentives import TokenFiatExchange, EconomyManager

class DummyBlockchain:
    def __init__(self):
        self.calls = []
    def send_earnings(self, amount, task_id, currency="PAIN"):
        self.calls.append((amount, task_id, currency))
        return f"tx-{task_id}"

def test_token_conversion():
    tokens = TokenFiatExchange.fiat_to_tokens(1.0)
    assert abs(TokenFiatExchange.tokens_to_fiat(tokens) - 1.0) < 1e-6

def test_reward_and_redeem():
    bc = DummyBlockchain()
    econ = EconomyManager(bc)
    record = econ.reward("node1", 5.0, "task1")
    assert record["tx_hash"] == "tx-task1"
    assert bc.calls == [(5.0, "task1", "PAIN")]
    assert econ.get_balance("node1") == 5.0
    payout = econ.redeem_tokens("node1", 2.0)
    assert payout["success"] is True
    assert abs(payout["payout"] - TokenFiatExchange.tokens_to_fiat(2.0)) < 1e-6
    assert econ.get_balance("node1") == 3.0


def test_staking_interest(monkeypatch):
    bc = DummyBlockchain()
    econ = EconomyManager(bc)
    econ.reward("n", 10.0, "t")

    # simulate passage of two days
    fake_time = [1000.0]

    def fake_now():
        return fake_time[0]

    monkeypatch.setattr("time.time", fake_now)
    econ.stake_tokens("n", 5.0)
    fake_time[0] += 2 * 86400
    result = econ.unstake_tokens("n")
    assert result["success"] is True
    assert result["interest"] > 0
    assert abs(econ.get_balance("n") - (10.0 + result["interest"])) < 1e-6
