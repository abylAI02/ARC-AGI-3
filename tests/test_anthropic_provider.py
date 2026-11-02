import tempfile
import unittest
from types import SimpleNamespace

from qahs.arc_cli import RUN_PARAMETERS, RESUME_DEFAULTS, build_parser
from qahs.arc_reasoner import ARC_REFLECTION_SCHEMA, OpenAIArcReasoner
from qahs.providers.anthropic_provider import AnthropicJSONCaller
from qahs.session import new_journal


def response(text='{"ok": true}', stop_reason="end_turn", category=None):
    return SimpleNamespace(
        content=[SimpleNamespace(type="thinking", thinking=""), SimpleNamespace(type="text", text=text)],
        stop_reason=stop_reason,
        stop_details=SimpleNamespace(category=category) if category else None,
        usage=SimpleNamespace(input_tokens=120, output_tokens=40, cache_read_input_tokens=0),
    )


class FakeClient:
    def __init__(self, *responses):
        self.responses = list(responses)
        self.requests = []
        self.messages = self

    def create(self, **kwargs):
        self.requests.append(kwargs)
        return self.responses.pop(0)


class AnthropicCallerTests(unittest.TestCase):
    def test_schema_effort_and_usage_are_sent_and_recorded(self):
        client = FakeClient(response())
        caller = AnthropicJSONCaller(model="claude-opus-5-5", effort="medium", client=client)
        self.assertEqual(caller.call_json("prompt", ARC_REFLECTION_SCHEMA, "arc_qahs_reflection"), {"ok": True})
        request = client.requests[0]
        self.assertEqual(request["model"], "claude-opus-5-5")
        self.assertEqual(request["output_config"]["format"], {"type": "json_schema", "schema": ARC_REFLECTION_SCHEMA})
        self.assertEqual(request["output_config"]["effort"], "medium")
        self.assertNotIn("temperature", request)
        self.assertNotIn("fallbacks", request)
        self.assertEqual(caller.last_usage["input_tokens"], 120)
        self.assertEqual(caller.settings["provider"], "anthropic")

    def test_refusal_and_truncation_raise(self):
        for bad in (response(stop_reason="refusal", category="cyber"), response(text='{"ok"', stop_reason="max_tokens")):
            caller = AnthropicJSONCaller(client=FakeClient(bad))
            with self.assertRaises(RuntimeError):
                caller.call_json("prompt", {})

    def test_reasoner_retries_a_refusal(self):
        client = FakeClient(response(stop_reason="refusal"), response('{"value": 3}'))
        reasoner = OpenAIArcReasoner(AnthropicJSONCaller(client=client), retry_delay=0)
        self.assertEqual(reasoner._request("p", {}, "n", lambda payload: payload["value"]), 3)
        self.assertEqual(reasoner.last_call_count, 2)
        self.assertEqual(reasoner.last_usage["input_tokens"], 240)


class ProviderCliTests(unittest.TestCase):
    def test_provider_flag(self):
        self.assertEqual(build_parser().parse_args([]).provider, "openai")
        self.assertEqual(build_parser().parse_args(["--provider", "anthropic"]).provider, "anthropic")

    def test_old_journal_without_provider_resumes_as_openai(self):
        with tempfile.TemporaryDirectory() as directory:
            journal = new_journal("ar25", directory)
            journal.append("run_started", source="arc", game="ar25", condition="compare", seed=0,
                           max_steps=3, frame_format="runs", arc_mode="offline")
            started = journal.first("run_started")
            params = {key: started[key] if key in started else RESUME_DEFAULTS[key] for key in RUN_PARAMETERS}
            self.assertEqual(params["provider"], "openai")


if __name__ == "__main__":
    unittest.main()
