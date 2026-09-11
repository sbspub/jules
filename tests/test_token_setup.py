from datetime import date

from shargent import token_setup


def test_token_is_current_requires_token_and_today_date():
    today = date(2026, 9, 10)
    assert token_setup.token_is_current(
        {"ZERODHA_ACCESS_TOKEN": "token", "ZERODHA_TOKEN_GENERATED_ON": "2026-09-10"}, today
    )
    assert not token_setup.token_is_current(
        {"ZERODHA_ACCESS_TOKEN": "token", "ZERODHA_TOKEN_GENERATED_ON": "2026-09-09"}, today
    )


def test_update_env_values_replaces_and_adds_without_losing_values(tmp_path):
    env_path = tmp_path / ".env"
    env_path.write_text("ZERODHA_API_KEY=key\nZERODHA_ACCESS_TOKEN=old\n")

    token_setup.update_env_values(
        env_path,
        {"ZERODHA_ACCESS_TOKEN": "new", "ZERODHA_TOKEN_GENERATED_ON": "2026-09-10"},
    )

    assert env_path.read_text() == (
        "ZERODHA_API_KEY=key\nZERODHA_ACCESS_TOKEN=new\nZERODHA_TOKEN_GENERATED_ON=2026-09-10\n"
    )


def test_setup_token_skips_interactive_login_when_current(tmp_path):
    env_path = tmp_path / ".env"
    env_path.write_text("ZERODHA_ACCESS_TOKEN=token\nZERODHA_TOKEN_GENERATED_ON=2026-09-10\n")
    messages = []

    renewed = token_setup.setup_token(
        env_path=env_path,
        today=date(2026, 9, 10),
        input_fn=lambda _: (_ for _ in ()).throw(AssertionError("should not prompt")),
        output_fn=messages.append,
    )

    assert not renewed
    assert "no renewal needed" in messages[0]
