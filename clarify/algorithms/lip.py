# SPDX-FileCopyrightText: 2026 Yang Zhang <zhangy2256@mail2.sysu.edu.cn>
#
# SPDX-License-Identifier: MIT

"""Frozen historical question_no_profile local source copy.
Exactly one public algorithm class; no new effectiveness measurement.

Team: lip
Team Members: Yang Zhang (Sun Yat-sen University), Zhen Wang (Sun Yat-sen University), Wenjie Hu (Sun Yat-sen University)
Main Contact: Yang Zhang <zhangy2256@mail2.sysu.edu.cn>
"""

from __future__ import annotations


def createImplementation():

    def _IBTypeName(value):
        actual = type(value)
        if actual in _IBOriginalTypeNames:
            return _IBOriginalTypeNames[actual]
        return str(actual).removeprefix("<class '").removesuffix("'>").rsplit(".", 1)[-1]

    def _IBInitializeConfig(self, config=None):
        overrides = dict(config or {})
        unknown = set(overrides) - set(self.DEFAULT_CONFIG)
        if unknown:
            raise ValueError(f"Unknown config option(s) for {_IBTypeName(self)}: {sorted(unknown)}")
        self.config = {**self.DEFAULT_CONFIG, **overrides}

    def _IBInitializeException(self, message):
        self.args = (message,)

    # Frozen source: pilot/submission_compare_20261031/snapshots/previous_submission.py
    # SPDX-FileCopyrightText: 2026 Yang Zhang <zhangy2256@mail2.sysu.edu.cn>
    #
    # SPDX-License-Identifier: MIT

    """IntentBridgeClarifier.

Propose a common program for plausible interpretations of the visible task and
audit its compatibility. On conflicting observable outputs, ask one atomic
behavioural question and synthesize afresh using the actual answer. Compatibility
audits are fallible model judgments, not access to hidden tests or formal proofs.

Team: lip
Team Members: Yang Zhang (Sun Yat-sen University), Zhen Wang (Sun Yat-sen University), Wenjie Hu (Sun Yat-sen University)
Main Contact: Yang Zhang <zhangy2256@mail2.sysu.edu.cn>
"""

    import ast as _V10Original_ast
    import json as _V10Original_json
    import re as _V10Original_re

    from clarify.baselines import (
        ClarificationAlgorithmBase as _V10Original_ClarificationAlgorithmBase,
    )
    from clarify.env import (
        LimitsExceededException as _V10Original_LimitsExceededException,
    )
    from clarify.env import (
        TooManyQuestionException as _V10Original_TooManyQuestionException,
    )

    def _V10Original_json_object(text):
        text = text.strip()
        if text.startswith("```"):
            text = "\n".join(text.splitlines()[1:-1])
        value = _V10Original_json.loads(text)
        if not isinstance(value, dict):
            raise ValueError("Expected object")
        return value

    def _V10Original_python_code(text, entry):
        match = _V10Original_re.search(r"```(?:python)?\s*\n(.*?)```", text, _V10Original_re.S)
        code = match.group(1) if match else text
        tree = _V10Original_ast.parse(code)
        if not any(
            isinstance(n, _V10Original_ast.FunctionDef) and n.name == entry for n in tree.body
        ):
            raise ValueError("Wrong entry point")
        return code

    class _V10Original__TaskRun:
        def record(self, **values):
            self.trace.append(values)

        def ask(self, env, question):
            if not isinstance(question, str) or not question.strip() or not env.can_ask():
                return ""
            try:
                return env.ask_human(question)
            except _V10Original_TooManyQuestionException:
                return ""

        def gate(self, env, problem):
            self.gate_attempted = True
            if not env.can_ask():
                return ""
            response = env.llm(
                "Review this Python task. Ask at most ONE atomic behavioral fact whose unknown value could cause failure. "
                'Do not ask for algorithms, test cases, style, or already stated facts. Return only JSON {"question":"..."}; '
                "use an empty string if clear.\n" + _V10Original_json.dumps(problem)
            )
            return _V10Original_json_object(response).get("question", "")

        def fallback(self, env, problem):
            if not self.qa[0] and not self.gate_attempted and env.can_ask():
                try:
                    question = self.gate(env, problem)
                    self.qa = (question, self.ask(env, question))
                except (ValueError, KeyError, TypeError, _V10Original_LimitsExceededException):
                    pass
            return self.solve(env, problem, *self.qa)

        def solve(self, env, problem, question="", answer="", note=""):
            question = question if isinstance(question, str) else ""
            answer = answer if isinstance(answer, str) else ""
            prompt = (
                "Implement exactly the entry_point in this task, even if names elsewhere differ. Return a complete fenced Python function.\n"
                + _V10Original_json.dumps(problem)
            )
            if question:
                prompt += (
                    "\nActual clarification question: "
                    + question
                    + "\nActual user answer: "
                    + answer
                )
                prompt += "\nThe actual answer supersedes only contradicted requirements; retain other explicit constraints."
            if note:
                prompt += "\nAuditable working state (not extra user requirements):\n" + note
            messages = [{"role": "user", "content": prompt}]
            for _attempt in range(self.config["repair_attempts"] + 1):
                text = env.llm(messages)
                try:
                    return _V10Original_python_code(text, problem["entry_point"])
                except (SyntaxError, ValueError):
                    messages += [
                        {"role": "assistant", "content": text},
                        {
                            "role": "user",
                            "content": "Return complete valid Python implementing exactly "
                            + problem["entry_point"]
                            + " in a python fence.",
                        },
                    ]
            return self.safe_fallback(problem)

        def robust_synthesis(self, env, problem):
            proposal = _V10Original_json_object(
                env.llm(
                    "Consider at most 3 plausible behavioral interpretations of the visible task. "
                    "Try to construct ONE whole program compatible with all, not a sampled program vote. If output requirements conflict, "
                    'give ONE atomic question resolving the conflict and a concrete witness. JSON {"worlds":["..."],"common_code":"complete Python or empty",'
                    '"compatibility_argument":"...","witness":null,"question":"..."}. Witness if conflicting: '
                    '{"input":"example input described as data","required_outputs":["output under interpretation 1","output under interpretation 2"]}. '
                    "No found witness does NOT prove compatibility. Ask no algorithms or hidden tests.\n"
                    + _V10Original_json.dumps(problem)
                )
            )
            common = proposal.get("common_code", "")
            if common and proposal.get("witness") is None:
                code = _V10Original_python_code(common, problem["entry_point"])
                self.last_code = code
                audit = _V10Original_json_object(
                    env.llm(
                        "Audit the proposed common implementation against each STATED interpretation. "
                        "This is a fallible compatibility check, not hidden-test validation. If any incompatible observable outputs exist, "
                        'return an atomic behavioral question. JSON {"compatible":true,"question":"","reason":"..."}. '
                        "Do not declare compatible merely because no tests failed.\n"
                        + _V10Original_json.dumps({"task": problem, "proposal": proposal})
                    )
                )
                if audit.get("compatible") is True and not audit.get("question"):
                    self.record(
                        status="applied",
                        route="proxy_common_program",
                        formal_compatibility_proved=False,
                    )
                    return code
                self.last_code = ""
                question = audit.get("question", "")
            else:
                question = proposal.get("question", "")
            answer = self.ask(env, question)
            self.qa = (question, answer)
            self.record(
                status="applied", route="conflict_question", formal_compatibility_proved=False
            )
            return self.solve(env, problem, question, answer)

        def safe_fallback(self, problem):
            return self.last_code or (
                "def "
                + problem["entry_point"]
                + "(*args, **kwargs):\n    raise NotImplementedError"
            )

        def execute(self, env, problem):
            self.trace = []
            self.qa = ("", "")
            self.gate_attempted = False
            self.last_code = ""
            try:
                return self.robust_synthesis(env, problem)
            except (
                ValueError,
                KeyError,
                TypeError,
                IndexError,
                AttributeError,
                SyntaxError,
                _V10Original_LimitsExceededException,
            ):
                try:
                    return self.fallback(env, problem)
                except _V10Original_LimitsExceededException:
                    return self.safe_fallback(problem)

    class _V10Original_IntentBridgeClarifier(_V10Original_ClarificationAlgorithmBase):
        DEFAULT_CONFIG = {
            # Extra attempts to obtain syntactically valid target-function code.
            "repair_attempts": 1,
        }

        def run(self, env, problem) -> str:
            repair_attempts = self.config["repair_attempts"]
            if type(repair_attempts) is not int or repair_attempts < 0:
                raise ValueError("repair_attempts must be a non-negative integer")
            # The harness may reuse the algorithm object across tasks.
            state = _V10Original__TaskRun()
            state.config = dict(self.config)
            visible = {"prompt": problem["prompt"], "entry_point": problem["entry_point"]}
            return state.execute(env, visible)

    # Frozen source: pilot/intentbridge_v2_20261101/algorithm.py
    """Evidence-grounded IntentBridge v2; only supplied environment methods execute code.

Generated checks and model reviews remain fallible consistency evidence.  This
module never reads a dataset, task identity, hidden field, reference program or
provider state.  Each invocation returns one program; speculative repairs do
not replace an earlier candidate without a strict, nonregressing improvement
on independently admitted visible checks.
"""

    import ast as _V10V2_ast
    import copy as _V10V2_copy
    import hashlib as _V10V2_hashlib
    import json as _V10V2_json
    import keyword as _V10V2_keyword
    import math as _V10V2_math
    import re as _V10V2_re

    from clarify.baselines import ClarificationAlgorithmBase as _V10V2_ClarificationAlgorithmBase
    from clarify.env import (
        LimitsExceededException as _V10V2_LimitsExceededException,
    )
    from clarify.env import (
        TooManyQuestionException as _V10V2_TooManyQuestionException,
    )

    _V10V2_BASE_POLICY = {"plan_guidance": "", "solve_guidance": ""}
    _V10V2_PROBE_PREFIX = "INTENTBRIDGE_V2_VISIBLE_CHECKS="
    _V10V2_MAX_CHECKS = 6
    _V10V2_TYPE_NAMES = {"none", "bool", "int", "float", "str", "list", "tuple", "dict"}

    _V10V2_GROUNDING = """Use ONLY the COMPLETE visible prompt, supplied entry_point and
literal actual question/answer. Missing information is UNKNOWN, not forbidden.
The supplied entry_point is the execution interface and cannot be revoked by a
simulated answer. An answer updates only the facts it addresses, including old
examples directly contradicted on those facts; retain unrelated constraints.
Never infer requirements from candidate code, remembered benchmarks, previous
tasks, hidden tests, a hypothetical interpretation, or model confidence. All
working summaries, probes and reviews are fallible, not extra requirements.
"""

    _V10V2_PLAN_INSTRUCTIONS = (
        _V10V2_GROUNDING
        + """Consider at most three plausible behavioral
interpretations. Try to construct ONE complete program compatible with them,
preserving IntentBridge's common-program bridge rather than voting over guesses.
Identify the consequential unresolved computation/interface decision on normal
legal inputs. There is no fixed priority for return type, name, signature or edge
cases. A missing signature does not mean no arguments. A witness illustrates
different hypotheses and does not confirm either. JSON {worlds:[string],
common_code:string,compatibility_argument:string,witness:null|object,
question:string,unresolved:[string]}. No witness is not proof of compatibility.
"""
    )

    _V10V2_QUESTION_INSTRUCTIONS = (
        _V10V2_GROUNDING
        + """Independently review the tentative bridge
and choose ONE neutral question about the unresolved fact most likely to change
the correct main computation. Use an asymmetric concrete legal input and
conditional outputs when useful. Include the COMPLETE concrete input or call
inside the actual question, never a reference such as 'the witness input' that
the user cannot see. A coherent rule can be one atomic question;
do not reject it just because its explanation contains several related words.
Do not presume unknown input arity/order or output shape. Do not mechanically
ask return type, repeat the prompt, or confirm an already supplied callable name
while a material behavioral choice remains. Do not request algorithms, hidden
requirements or tests. If all material behavior is explicit, one task-specific
confirmation is allowed; no generic fallback question. JSON {question:string,
target:string,mode:'uncertainty'|'confirmation'|'none',reason:string}.
"""
    )

    _V10V2_BRIEF_INSTRUCTIONS = (
        _V10V2_GROUNDING
        + """Write a SHORT implementation brief. Separate
confirmed requirements, answer-scoped updates, and unresolved facts. Every fact
needs an exact nonempty quote from prompt or actual_answer; each scope update
must cite actual_answer. Do not turn an unknown interface into a prohibition,
or let a narrow answer waive unrelated facts. JSON {confirmed:[{fact:string,
evidence:[{source:'prompt'|'actual_answer',quote:string}]}],
scope_updates:[{fact:string,evidence:[{source:'prompt'|'actual_answer',quote:string}]}],
unresolved:[string]}. A malformed brief will be discarded; the complete original
task and literal Q/A always remain authoritative.
"""
    )

    _V10V2_SOLVE_INSTRUCTIONS = (
        _V10V2_GROUNDING
        + """Return one complete fenced Python program
implementing exactly entry_point. Read all visible examples. Apply the SAME
confirmed requirements to every implementation candidate; do not sample guesses
of different user intent. Infer signature only from visible evidence and current
Q/A. Respect nested Python types, bool versus int, whitespace, return versus
printing, mutation constraints and normal legal inputs when they are specified.
Do not add a runtime argument-adaptation wrapper or silently drop/reorder/fill
call arguments. A brief schema failure is not a reason to abandon the task.
For a repair, first use the supplied diagnosis and real execution observations,
make a targeted change, and retain all other confirmed requirements. Generated
expected values and review assertions can be wrong; unsupported ones must be
discarded rather than forced into the implementation. Never ask another human.
"""
    )

    _V10V2_TYPED_INSTRUCTIONS = """TYPED is {type:'none'},
{type:'bool'|'int'|'float'|'str',value:VALUE},
{type:'list'|'tuple',items:[TYPED]}, or
{type:'dict',items:[{key:TYPED,value:TYPED}]}. Tag EVERY nested value. Preserve
tuple/list and bool/int; plain JSON arrays do not represent Python tuples.
"""

    _V10V2_CHECK_INSTRUCTIONS = (
        _V10V2_GROUNDING
        + """Propose at most FOUR self-contained executable
checks without seeing any candidate. Use current visible examples first, then
entailed boundary cases/properties within a known legal input domain. Exact
Python type needs evidence too. If only a mathematical numeric value is known,
use numeric_value instead of imposing int versus float. Distinguish printed
stdout from the function's return; do not assert an unknown return for a print
task. Conflicting or unsupported checks must be omitted. Every check needs
evidence and a derivation, not merely a related quote.
JSON {checks:[{id:string,args:[TYPED],kwargs:{name:TYPED},
kind:'exact',target:'return'|'stdout',expected:TYPED,evidence:[{source:
'prompt'|'actual_answer',quote:string}],derivation:string} OR
{id:string,args:[TYPED],kwargs:{name:TYPED},kind:'property',
property:{name:'return_type',type:TYPE} OR
{name:'length_equals_input',input:{arg:INDEX}|{kwarg:NAME}} OR
{name:'same_type_as_input',input:{arg:INDEX}|{kwarg:NAME}} OR
{name:'nonmutation'} OR {name:'numeric_value',expected:TYPED},
evidence:[{source:'prompt'|'actual_answer',quote:string}],derivation:string}]}.
TYPE is none/bool/int/float/str/list/tuple/dict. numeric_value permits int/float
equality but excludes bool; it is not a tolerance rule. Use checks:[] if none
is fully supported. Do not invent properties from category conventions.
"""
        + _V10V2_TYPED_INSTRUCTIONS
    )

    _V10V2_REVIEW_INSTRUCTIONS = (
        _V10V2_GROUNDING
        + """Independently review candidate and checks.
Admit a check only if its legal input, expected value/property, channel and any
type assumption follow from current visible evidence. Reject stale examples,
contradicted arity, guessed types/domains and unsupported properties. A quote
alone is not an entailment proof. Check main computation and interface without
fixed category priority. Describe only concrete evidence-backed defects; model
self-confidence is not a trigger. Convert a justified counterexample or defect
into at most TWO additional grounded checks when possible, using the exact
check schema provided. These additions receive a separate independent review.
JSON {accepted_check_ids:[string],issues:[{id:string,defect:string,
evidence:[{source:'prompt'|'actual_answer',quote:string}],check_ids:[string]}],
additional_checks:[CHECK],unresolved:[string],reason:string}.
Passing checks and agreement are not semantic correctness proofs.
Additional CHECK schema: {id:string,args:[TYPED],kwargs:{name:TYPED},
kind:'exact',target:'return'|'stdout',expected:TYPED,evidence:[{source:
'prompt'|'actual_answer',quote:string}],derivation:string} OR
{id:string,args:[TYPED],kwargs:{name:TYPED},kind:'property',
property:{name:'return_type',type:TYPE} OR
{name:'length_equals_input',input:{arg:INDEX}|{kwarg:NAME}} OR
{name:'same_type_as_input',input:{arg:INDEX}|{kwarg:NAME}} OR
{name:'nonmutation'} OR {name:'numeric_value',expected:TYPED},
evidence:[{source:'prompt'|'actual_answer',quote:string}],derivation:string}.
TYPE is none/bool/int/float/str/list/tuple/dict. A generally stated rule can
entail a new legal input instance; admission is not limited to copying examples.
"""
        + _V10V2_TYPED_INSTRUCTIONS
    )

    _V10V2_ADMISSION_INSTRUCTIONS = (
        _V10V2_GROUNDING
        + """Independently decide which proposed
checks are fully entailed, without seeing candidate code or execution results.
Recompute derivations, preserve nested types, and distinguish stdout/return.
Reject a property without evidence, invented domains, stale answer scope,
counterexamples with unsupported expected values, and numeric type assumptions.
JSON {accepted_check_ids:[string],reason:string}. A previous reviewer or failed
probe is not authority to add requirements. A generally stated rule can entail
a new legal instance; do not restrict admission to copied prompt examples.
"""
    )

    _V10V2_DIAGNOSE_INSTRUCTIONS = (
        _V10V2_GROUNDING
        + """Using real sandbox values/exceptions and
the independently admitted checks, explain the concrete failure path briefly.
First consider whether the check itself is unsupported or stale. If so request
challenge_checks; it will be independently re-reviewed before any code change.
Otherwise propose a targeted implementation repair grounded in exact evidence.
Review issues alone must be explicit evidence-backed defects, not confidence.
JSON {action:'repair'|'challenge_checks'|'stop',diagnosis:string,target:string,
evidence:[{source:'prompt'|'actual_answer',quote:string}],
challenged_check_ids:[string]}. Do not change intent, invent expected outputs,
relax confirmed facts, or ask another question. No useful change => stop.
"""
    )

    def _V10V2_validate_policy(value):
        if not isinstance(value, dict) or set(value) != set(_V10V2_BASE_POLICY):
            raise ValueError("policy_requires_plan_and_solve_guidance")
        for text in value.values():
            if not isinstance(text, str) or len(text) > 3000:
                raise ValueError("invalid_policy_guidance")
            if _V10V2_re.search(
                r"HumanEval|Mbpp|MBPP|task_id|https?://|\bdef\s+|\bassert\s+|```", text
            ):
                raise ValueError("task_specific_or_executable_guidance_forbidden")
        return _V10V2_copy.deepcopy(value)

    def _V10V2_qa_hash(problem, question, answer):
        value = {
            "prompt": problem["prompt"],
            "entry_point": problem["entry_point"],
            "actual_question": question,
            "actual_answer": answer,
        }
        return _V10V2_hashlib.sha256(
            _V10V2_json.dumps(
                value, sort_keys=True, ensure_ascii=False, separators=(",", ":")
            ).encode("utf-8")
        ).hexdigest()

    def _V10V2_decode_typed(value):
        if not isinstance(value, dict) or not isinstance(value.get("type"), str):
            raise ValueError("typed_value_requires_type_tag")
        tag = value["type"]
        if tag == "none" and set(value) == {"type"}:
            return None
        scalar_types = {"bool": bool, "int": int, "float": float, "str": str}
        if tag in scalar_types and set(value) == {"type", "value"}:
            result = value["value"]
            if type(result) is not scalar_types[tag] or (
                tag == "float" and not _V10V2_math.isfinite(result)
            ):
                raise ValueError("typed_scalar_value_mismatch")
            return result
        if tag in {"list", "tuple"} and set(value) == {"type", "items"}:
            if not isinstance(value["items"], list):
                raise ValueError("typed_container_items_required")
            values = [_V10V2_decode_typed(v) for v in value["items"]]
            return tuple(values) if tag == "tuple" else values
        if tag == "dict" and set(value) == {"type", "items"}:
            if not isinstance(value["items"], list):
                raise ValueError("typed_dictionary_items_required")
            result = {}
            for pair in value["items"]:
                if not isinstance(pair, dict) or set(pair) != {"key", "value"}:
                    raise ValueError("typed_dictionary_pair_invalid")
                key = _V10V2_decode_typed(pair["key"])
                try:
                    if key in result:
                        raise ValueError("duplicate_or_colliding_dictionary_key")
                    result[key] = _V10V2_decode_typed(pair["value"])
                except TypeError:
                    raise ValueError("unhashable_dictionary_key") from None
            return result
        raise ValueError("unsupported_typed_value")

    def _V10V2_validate_evidence(value, problem, answer, *, answer_required=False):
        if not isinstance(value, list) or not value:
            raise ValueError("source_evidence_required")
        for quote in value:
            if not isinstance(quote, dict) or set(quote) != {"source", "quote"}:
                raise ValueError("invalid_evidence_object")
            if quote["source"] not in {"prompt", "actual_answer"}:
                raise ValueError("invalid_evidence_source")
            source = problem["prompt"] if quote["source"] == "prompt" else answer
            if (
                not isinstance(quote["quote"], str)
                or not quote["quote"].strip()
                or quote["quote"] not in source
            ):
                raise ValueError("evidence_quote_not_exact")
        if answer_required and not any(q["source"] == "actual_answer" for q in value):
            raise ValueError("scope_update_requires_actual_answer_evidence")
        return _V10V2_copy.deepcopy(value)

    def _V10V2_validate_brief(value, problem, answer):
        if not isinstance(value, dict) or set(value) != {
            "confirmed",
            "scope_updates",
            "unresolved",
        }:
            raise ValueError("brief_schema_invalid")
        for field in ("confirmed", "scope_updates"):
            if not isinstance(value[field], list):
                raise ValueError("brief_facts_invalid")
            for item in value[field]:
                if (
                    not isinstance(item, dict)
                    or set(item) != {"fact", "evidence"}
                    or not isinstance(item["fact"], str)
                    or not item["fact"].strip()
                ):
                    raise ValueError("brief_fact_invalid")
                _V10V2_validate_evidence(
                    item["evidence"], problem, answer, answer_required=field == "scope_updates"
                )
        if not isinstance(value["unresolved"], list) or not all(
            isinstance(s, str) for s in value["unresolved"]
        ):
            raise ValueError("brief_unknowns_invalid")
        return _V10V2_copy.deepcopy(value)

    def _V10V2__input_ref(value, check):
        if not isinstance(value, dict):
            raise ValueError("input_reference_invalid")
        if (
            set(value) == {"arg"}
            and type(value["arg"]) is int
            and 0 <= value["arg"] < len(check["args"])
        ):
            return
        if (
            set(value) == {"kwarg"}
            and isinstance(value["kwarg"], str)
            and value["kwarg"] in check["kwargs"]
        ):
            return
        raise ValueError("input_reference_invalid")

    def _V10V2_validate_checks(value, problem, answer, *, existing_ids=(), limit=_V10V2_MAX_CHECKS):
        # fmt: off
        """Return admitted-schema proposals and explicit structural rejection reasons.

    Source matching is a necessary mechanical gate. Independent model admission
    still has to judge entailment; this function does not claim to prove it.
    """
        # fmt: on
        if not isinstance(value, dict) or not isinstance(value.get("checks"), list):
            raise ValueError("checks_array_required")
        good, rejected, used = [], [], set(existing_ids)
        for position, check in enumerate(value["checks"]):
            ident = check.get("id", "") if isinstance(check, dict) else ""
            try:
                if position >= limit:
                    raise ValueError("check_limit_exceeded")
                if not isinstance(ident, str) or not ident.strip() or ident in used:
                    raise ValueError("check_id_missing_or_duplicate")
                if not isinstance(check.get("args"), list) or not isinstance(
                    check.get("kwargs"), dict
                ):
                    raise ValueError("check_arguments_invalid")
                if not all(
                    isinstance(k, str) and k.isidentifier() and not _V10V2_keyword.iskeyword(k)
                    for k in check["kwargs"]
                ):
                    raise ValueError("keyword_name_invalid")
                for item in [*check["args"], *check["kwargs"].values()]:
                    _V10V2_decode_typed(item)
                _V10V2_validate_evidence(check["evidence"], problem, answer)
                if not isinstance(check.get("derivation"), str) or not check["derivation"].strip():
                    raise ValueError("check_derivation_required")
                shared = {"id", "args", "kwargs", "kind", "evidence", "derivation"}
                if check.get("kind") == "exact":
                    if set(check) != shared | {"target", "expected"} or check["target"] not in {
                        "return",
                        "stdout",
                    }:
                        raise ValueError("exact_check_schema_invalid")
                    expected = _V10V2_decode_typed(check["expected"])
                    if check["target"] == "stdout" and type(expected) is not str:
                        raise ValueError("stdout_expectation_must_be_string")
                elif check.get("kind") == "property":
                    if set(check) != shared | {"property"} or not isinstance(
                        check["property"], dict
                    ):
                        raise ValueError("property_check_schema_invalid")
                    prop = check["property"]
                    name = prop.get("name")
                    if (
                        name == "return_type"
                        and set(prop) == {"name", "type"}
                        and prop["type"] in _V10V2_TYPE_NAMES
                    ):
                        pass
                    elif name in {"length_equals_input", "same_type_as_input"} and set(prop) == {
                        "name",
                        "input",
                    }:
                        _V10V2__input_ref(prop["input"], check)
                    elif name == "nonmutation" and set(prop) == {"name"}:
                        pass
                    elif name == "numeric_value" and set(prop) == {"name", "expected"}:
                        if type(_V10V2_decode_typed(prop["expected"])) not in {int, float}:
                            raise ValueError("numeric_property_requires_number_not_bool")
                    else:
                        raise ValueError("unsupported_property")
                else:
                    raise ValueError("unsupported_check_kind")
                _V10V2_json.dumps(check, allow_nan=False)
            except (KeyError, TypeError, ValueError, RecursionError) as error:
                rejected.append({"id": ident, "reason": str(error)})
                continue
            good.append(_V10V2_copy.deepcopy(check))
            used.add(ident)
        return good, rejected

    def _V10V2__signature(arguments):
        return {
            "positional_only": [a.arg for a in arguments.posonlyargs],
            "positional": [a.arg for a in arguments.args],
            "keyword_only": [a.arg for a in arguments.kwonlyargs],
            "vararg": arguments.vararg.arg if arguments.vararg else None,
            "varkw": arguments.kwarg.arg if arguments.kwarg else None,
            "defaults": [_V10V2_ast.dump(x, include_attributes=False) for x in arguments.defaults],
            "keyword_defaults": [
                _V10V2_ast.dump(x, include_attributes=False) if x is not None else None
                for x in arguments.kw_defaults
            ],
        }

    def _V10V2_parse_candidate(text, problem):
        code = _V10Original_python_code(text, problem["entry_point"])
        # AST parsing alone accepts e.g. a module-level return or a break outside
        # a loop. Compile only; no candidate is executed on the host.
        compile(code, "<visible-candidate-structure>", "exec")
        tree = _V10V2_ast.parse(code)
        targets = [
            n
            for n in tree.body
            if isinstance(n, (_V10V2_ast.FunctionDef, _V10V2_ast.AsyncFunctionDef))
            and n.name == problem["entry_point"]
        ]
        if len(targets) != 1 or not isinstance(targets[0], _V10V2_ast.FunctionDef):
            raise ValueError("exactly_one_synchronous_supplied_entry_point_required")
        try:
            visible_tree = _V10V2_ast.parse(problem["prompt"])
        except (SyntaxError, ValueError):
            return code
        functions = [n for n in visible_tree.body if isinstance(n, _V10V2_ast.FunctionDef)]
        explicit = next((n for n in functions if n.name == problem["entry_point"]), None)
        if explicit is None and len(functions) == 1:
            only = functions[0]
            if all(
                isinstance(n, _V10V2_ast.Pass)
                or isinstance(n, _V10V2_ast.Expr)
                and isinstance(n.value, _V10V2_ast.Constant)
                and (isinstance(n.value.value, str) or n.value.value is Ellipsis)
                for n in only.body
            ):
                explicit = only
        if explicit is not None and _V10V2__signature(explicit.args) != _V10V2__signature(
            targets[0].args
        ):
            raise ValueError(
                "visible_signature_mismatch: "
                + _V10V2_json.dumps(_V10V2__signature(explicit.args), sort_keys=True)
            )
        return code

    def _V10V2_probe_script(code, entry_point, checks):
        """Generate a sandbox script. Never execute candidate code on the host."""
        cases = []
        for check in checks:
            case = {
                "id": check["id"],
                "kind": check["kind"],
                "args": [_V10V2_decode_typed(x) for x in check["args"]],
                "kwargs": {k: _V10V2_decode_typed(v) for k, v in check["kwargs"].items()},
            }
            if check["kind"] == "exact":
                case.update(target=check["target"], expected=_V10V2_decode_typed(check["expected"]))
            else:
                case["property"] = _V10V2_copy.deepcopy(check["property"])
                if case["property"]["name"] == "numeric_value":
                    case["property"]["expected"] = _V10V2_decode_typed(case["property"]["expected"])
            cases.append(case)
        return (
            """import json as _ib_json
import copy as _ib_copy
import io as _ib_io
import contextlib as _ib_contextlib
import traceback as _ib_traceback
import math as _ib_math
def _ib_typed(value, ancestors=()):
    if value is None:
        return {'type': 'none'}
    kind = type(value)
    if kind in (bool, int, str) or kind is float and _ib_math.isfinite(value):
        return {'type': kind.__name__, 'value': value}
    if id(value) in ancestors:
        return {'type': 'unsupported', 'python_type': kind.__name__, 'repr': '<cycle>'}
    path = ancestors + (id(value),)
    if kind in (tuple, list):
        return {'type': kind.__name__, 'items': [_ib_typed(v, path) for v in value]}
    if kind is dict:
        return {'type': 'dict', 'items': [{'key': _ib_typed(k, path), 'value': _ib_typed(v, path)} for k, v in value.items()]}
    return {'type': 'unsupported', 'python_type': kind.__name__, 'repr': repr(value)}
def _ib_equal(a, b):
    if type(a) is not type(b):
        return False
    if type(a) in (list, tuple):
        return len(a) == len(b) and all(_ib_equal(x, y) for x, y in zip(a, b))
    if type(a) is dict:
        return len(a) == len(b) and all(any(_ib_equal(k, other) and _ib_equal(v, a[other]) for other in a) for k, v in b.items())
    return a == b
def _ib_reference(ref, args, kwargs):
    return args[ref['arg']] if 'arg' in ref else kwargs[ref['kwarg']]
_ib_records = []
for _ib_case in """
            + repr(cases)
            + """:
    _ib_capture = _ib_io.StringIO()
    _ib_record = {'id': _ib_case['id']}
    try:
        _ib_before_args = _ib_copy.deepcopy(_ib_case['args'])
        _ib_before_kwargs = _ib_copy.deepcopy(_ib_case['kwargs'])
        _ib_record['inputs_before'] = _ib_typed((_ib_before_args, _ib_before_kwargs))
        with _ib_contextlib.redirect_stdout(_ib_capture):
            _ib_ns = {}
            exec(compile("""
            + repr(code)
            + """, '<visible-candidate>', 'exec'), _ib_ns)
            _ib_actual = _ib_ns["""
            + repr(entry_point)
            + """](*_ib_case['args'], **_ib_case['kwargs'])
        _ib_stdout = _ib_capture.getvalue()
        _ib_record.update(actual=_ib_typed(_ib_actual), actual_type=type(_ib_actual).__name__, stdout=_ib_stdout,
                          inputs_after=_ib_typed((_ib_case['args'], _ib_case['kwargs'])))
        if _ib_case['kind'] == 'exact':
            _ib_observed = _ib_actual if _ib_case['target'] == 'return' else _ib_stdout
            _ib_expected = _ib_case['expected']
            _ib_ok = _ib_equal(_ib_observed, _ib_expected)
            _ib_record['difference'] = {'target': _ib_case['target'], 'expected': _ib_typed(_ib_expected),
                                      'actual': _ib_typed(_ib_observed), 'same_type': type(_ib_observed) is type(_ib_expected)}
        else:
            _ib_prop = _ib_case['property']
            _ib_name = _ib_prop['name']
            if _ib_name == 'return_type':
                _ib_ok = ('none' if _ib_actual is None else type(_ib_actual).__name__) == _ib_prop['type']
            elif _ib_name == 'length_equals_input':
                _ib_ref = _ib_reference(_ib_prop['input'], _ib_before_args, _ib_before_kwargs)
                _ib_ok = len(_ib_actual) == len(_ib_ref)
            elif _ib_name == 'same_type_as_input':
                _ib_ref = _ib_reference(_ib_prop['input'], _ib_before_args, _ib_before_kwargs)
                _ib_ok = type(_ib_actual) is type(_ib_ref)
            elif _ib_name == 'nonmutation':
                _ib_ok = _ib_equal(_ib_before_args, _ib_case['args']) and _ib_equal(_ib_before_kwargs, _ib_case['kwargs'])
            elif _ib_name == 'numeric_value':
                _ib_ok = type(_ib_actual) in (int, float) and _ib_actual == _ib_prop['expected']
            else:
                raise ValueError('unsupported admitted property')
            _ib_record['difference'] = {'property': _ib_prop, 'satisfied': bool(_ib_ok)}
        _ib_record['status'] = 'pass' if _ib_ok else 'fail'
    except Exception as _ib_error:
        _ib_record.update(status='error', error_type=type(_ib_error).__name__, error_message=str(_ib_error),
                          traceback=_ib_traceback.format_exc(), stdout=_ib_capture.getvalue())
    _ib_records.append(_ib_record)
print("""
            + repr(_V10V2_PROBE_PREFIX)
            + """ + _ib_json.dumps(_ib_records, allow_nan=False))
"""
        )

    def _V10V2__observation_typed(value):
        if isinstance(value, dict) and value.get("type") == "unsupported":
            return (
                set(value) == {"type", "python_type", "repr"}
                and isinstance(value["python_type"], str)
                and isinstance(value["repr"], str)
            )
        if (
            isinstance(value, dict)
            and value.get("type") in {"list", "tuple"}
            and set(value) == {"type", "items"}
        ):
            return isinstance(value["items"], list) and all(
                _V10V2__observation_typed(v) for v in value["items"]
            )
        if (
            isinstance(value, dict)
            and value.get("type") == "dict"
            and set(value) == {"type", "items"}
        ):
            return isinstance(value["items"], list) and all(
                isinstance(p, dict)
                and set(p) == {"key", "value"}
                and _V10V2__observation_typed(p["key"])
                and _V10V2__observation_typed(p["value"])
                for p in value["items"]
            )
        try:
            _V10V2_decode_typed(value)
            return True
        except (TypeError, ValueError, RecursionError):
            return False

    def _V10V2_parse_observations(raw, checks):
        if not isinstance(raw, str):
            return None
        lines = [
            line[len(_V10V2_PROBE_PREFIX) :]
            for line in raw.splitlines()
            if line.startswith(_V10V2_PROBE_PREFIX)
        ]
        if len(lines) != 1:
            return None
        try:
            rows = _V10V2_json.loads(lines[0])
            if not isinstance(rows, list) or len(rows) != len(checks):
                return None
            if [r.get("id") if isinstance(r, dict) else None for r in rows] != [
                c["id"] for c in checks
            ]:
                return None
            for row in rows:
                if row.get("status") in {"pass", "fail"}:
                    if (
                        not _V10V2__observation_typed(row.get("actual"))
                        or not isinstance(row.get("actual_type"), str)
                        or not isinstance(row.get("stdout"), str)
                        or not isinstance(row.get("difference"), dict)
                    ):
                        return None
                elif row.get("status") == "error":
                    if not isinstance(row.get("error_type"), str) or not isinstance(
                        row.get("error_message"), str
                    ):
                        return None
                else:
                    return None
            return _V10V2_copy.deepcopy(rows)
        except (TypeError, ValueError, RecursionError):
            return None

    class _V10V2__Run:
        def __init__(self, config, policy, problem, *, conditioned=False):
            self.config, self.policy, self.problem = config, policy, problem
            self.trace, self.qa, self.asked, self.epoch = [], ("", ""), False, 0
            self.digest, self.best = _V10V2_qa_hash(problem, "", ""), None
            self.artifacts = {
                "variant": "intentbridge_v2",
                "policy": _V10V2_copy.deepcopy(policy),
                "conditioned_actual_qa": conditioned,
                "proposal": {},
                "question_meta": {},
                "qa_events": [],
                "implementation_brief": {},
                "checks": {"proposed": [], "admitted": [], "rejected": [], "reviews": []},
                "reviews": [],
                "candidates": [],
                "probe_runs": [],
                "diagnoses": [],
                "rounds": [],
                "selection": {},
                "mechanisms": {
                    "question_attempted": 0,
                    "brief_valid": 0,
                    "brief_fallback": 0,
                    "format_repairs": 0,
                    "candidate_slots": 0,
                    "valid_candidates": 0,
                    "generation_requests": 0,
                    "code_format_rejections": 0,
                    "check_proposed": 0,
                    "check_admitted": 0,
                    "check_rejected": 0,
                    "check_challenged": 0,
                    "probe_runs": 0,
                    "repair_triggers": 0,
                    "repair_generated": 0,
                    "structural_recovery_triggers": 0,
                    "check_failure_triggers": 0,
                    "review_defect_triggers": 0,
                    "repair_accepted": 0,
                    "repair_rejected": 0,
                },
                "semantic_proof": False,
            }

        def record(self, **values):
            self.trace.append(values)

        def count(self, key, amount=1):
            self.artifacts["mechanisms"][key] += amount

        def context(self):
            return {
                "task": self.problem,
                "actual_question": self.qa[0],
                "actual_answer": self.qa[1],
                "qa_epoch": self.epoch,
                "qa_hash": self.digest,
                "implementation_brief_fallible": self.artifacts["implementation_brief"],
            }

        def guidance(self, field):
            text = self.policy[field]
            return "\nAdditional TRAIN-derived general guidance:\n" + text + "\n" if text else ""

        def json_call(self, env, instructions, payload, phase, validator=None):
            messages = [
                {
                    "role": "user",
                    "content": instructions + _V10V2_json.dumps(payload, ensure_ascii=False),
                }
            ]
            for attempt in range(self.config["repair_attempts"] + 1):
                # Transport/configuration exceptions must escape, including ValueError.
                raw = env.llm(messages)
                try:
                    data = _V10Original_json_object(raw)
                    return validator(data) if validator is not None else data
                except (AttributeError, KeyError, TypeError, ValueError, RecursionError) as error:
                    self.record(
                        phase=phase, status="format_error", attempt=attempt, detail=str(error)
                    )
                    if attempt < self.config["repair_attempts"]:
                        self.count("format_repairs")
                        messages.extend(
                            [
                                {
                                    "role": "assistant",
                                    "content": raw if isinstance(raw, str) else "",
                                },
                                {
                                    "role": "user",
                                    "content": "Repair only the requested JSON schema: "
                                    + str(error)
                                    + ". Preserve the COMPLETE original task and literal actual Q/A; do not invent requirements.",
                                },
                            ]
                        )
            self.record(phase=phase, status="format_exhausted")
            return None

        def set_qa(self, question, answer, *, status):
            self.asked, self.epoch, self.qa = True, self.epoch + 1, (question, answer)
            self.digest = _V10V2_qa_hash(self.problem, question, answer)
            # Clearing selection is essential even when the answer is empty.
            self.best = None
            self.artifacts["qa_events"].append(
                {
                    "question": question,
                    "answer": answer,
                    "status": status,
                    "qa_epoch": self.epoch,
                    "qa_hash": self.digest,
                }
            )

        def plan_and_ask(self, env):
            proposal = (
                self.json_call(
                    env,
                    _V10V2_PLAN_INSTRUCTIONS + self.guidance("plan_guidance"),
                    self.context(),
                    "interpretation_bridge",
                )
                or {}
            )
            self.artifacts["proposal"] = _V10V2_copy.deepcopy(proposal)
            if not env.can_ask():
                return

            def question_schema(value):
                if (
                    not isinstance(value.get("question"), str)
                    or not isinstance(value.get("target"), str)
                    or not isinstance(value.get("reason"), str)
                    or value.get("mode") not in {"uncertainty", "confirmation", "none"}
                ):
                    raise ValueError("question_schema_invalid")
                if value["mode"] == "none" and value["question"].strip():
                    raise ValueError("question_none_mode_requires_empty_text")
                return value

            meta = self.json_call(
                env,
                _V10V2_QUESTION_INSTRUCTIONS + self.guidance("plan_guidance"),
                {**self.context(), "tentative_bridge": proposal},
                "question_selection",
                question_schema,
            )
            self.artifacts["question_meta"] = _V10V2_copy.deepcopy(meta or {})
            question = meta.get("question", "") if meta else ""
            if not question.strip() or self.asked or not env.can_ask():
                return
            self.count("question_attempted")
            # Invalidate all pre-answer state before the real interaction starts.
            self.set_qa(question, "", status="attempted")
            try:
                answer = env.ask_human(question)
            except _V10V2_TooManyQuestionException:
                self.artifacts["qa_events"][-1]["status"] = "environment_refused"
                return
            if not isinstance(answer, str):
                raise TypeError("actual_answer_must_be_string")
            self.qa = (question, answer)
            self.digest = _V10V2_qa_hash(self.problem, question, answer)
            self.artifacts["qa_events"][-1].update(
                answer=answer, status="completed", qa_hash=self.digest
            )

        def brief(self, env):
            value = self.json_call(
                env,
                _V10V2_BRIEF_INSTRUCTIONS,
                self.context(),
                "implementation_brief",
                lambda v: _V10V2_validate_brief(v, self.problem, self.qa[1]),
            )
            if value is None:
                value = {
                    "confirmed": [],
                    "scope_updates": [],
                    "unresolved": [
                        "Structured brief unavailable; use the complete original task and literal Q/A."
                    ],
                    "fallback": True,
                }
                self.count("brief_fallback")
            else:
                value["fallback"] = False
                self.count("brief_valid")
            value.update(qa_epoch=self.epoch, qa_hash=self.digest)
            self.artifacts["implementation_brief"] = value

        def generate(self, env, trigger, diagnosis=None):
            slot = len(self.artifacts["candidates"])
            if slot >= self.config["max_candidates"]:
                return None
            candidate = {
                "candidate_id": "candidate_" + str(slot),
                "qa_epoch": self.epoch,
                "qa_hash": self.digest,
                "trigger": _V10V2_copy.deepcopy(trigger),
                "code": "",
                "eligible": False,
                "format_errors": [],
                "observations": None,
            }
            self.artifacts["candidates"].append(candidate)
            self.count("candidate_slots")
            payload = {
                **self.context(),
                "trigger": trigger,
                "selected_candidate": _V10V2_copy.deepcopy(self.best),
                "diagnosis": diagnosis,
                "admitted_checks_fallible": self.artifacts["checks"]["admitted"],
                "previous_attempts": [
                    {k: c[k] for k in ("candidate_id", "code", "observations", "eligible")}
                    for c in self.artifacts["candidates"][:-1]
                ],
            }
            messages = [
                {
                    "role": "user",
                    "content": _V10V2_SOLVE_INSTRUCTIONS
                    + self.guidance("solve_guidance")
                    + _V10V2_json.dumps(payload, ensure_ascii=False),
                }
            ]
            for attempt in range(self.config["repair_attempts"] + 1):
                self.count("generation_requests")
                raw = env.llm(messages)
                try:
                    code = _V10V2_parse_candidate(raw, self.problem)
                except (SyntaxError, TypeError, ValueError, AttributeError) as error:
                    event = {"attempt": attempt, "error": _IBTypeName(error), "detail": str(error)}
                    candidate["format_errors"].append(event)
                    self.count("code_format_rejections")
                    self.record(
                        phase="generation",
                        status="format_error",
                        candidate_id=candidate["candidate_id"],
                        **event,
                    )
                    if attempt < self.config["repair_attempts"]:
                        self.count("format_repairs")
                        messages.extend(
                            [
                                {
                                    "role": "assistant",
                                    "content": raw if isinstance(raw, str) else "",
                                },
                                {
                                    "role": "user",
                                    "content": "Repair this structural error: "
                                    + str(error)
                                    + ". Return a complete Python fence implementing exactly "
                                    + self.problem["entry_point"]
                                    + ". Preserve the same complete task, actual Q/A, scoped updates and implementation intent. No additional human question.",
                                },
                            ]
                        )
                    continue
                candidate.update(
                    code=code,
                    eligible=True,
                    code_sha256=_V10V2_hashlib.sha256(code.encode("utf-8")).hexdigest(),
                )
                self.count("valid_candidates")
                if slot:
                    self.count("repair_generated")
                return candidate
            candidate["rejection_reason"] = "structural_format_exhausted"
            return None

        def checks_from(self, value, *, limit, existing_ids=()):
            try:
                proposals, rejected = _V10V2_validate_checks(
                    value, self.problem, self.qa[1], existing_ids=existing_ids, limit=limit
                )
            except (TypeError, ValueError):
                proposals, rejected = [], [{"id": "", "reason": "checks_schema_unavailable"}]
            self.artifacts["checks"]["proposed"].extend(_V10V2_copy.deepcopy(proposals))
            self.artifacts["checks"]["rejected"].extend(rejected)
            self.count("check_proposed", len(proposals) + len(rejected))
            self.count("check_rejected", len(rejected))
            return proposals

        def valid_issues(self, value):
            result = []
            if not isinstance(value, list):
                return result
            for issue in value:
                try:
                    if (
                        not isinstance(issue, dict)
                        or not isinstance(issue.get("id"), str)
                        or not issue["id"].strip()
                        or not isinstance(issue.get("defect"), str)
                        or not issue["defect"].strip()
                    ):
                        raise ValueError("issue_schema_invalid")
                    _V10V2_validate_evidence(issue["evidence"], self.problem, self.qa[1])
                    if not isinstance(issue.get("check_ids"), list) or not all(
                        isinstance(s, str) for s in issue["check_ids"]
                    ):
                        raise ValueError("issue_check_ids_invalid")
                except (KeyError, TypeError, ValueError):
                    continue
                result.append(_V10V2_copy.deepcopy(issue))
            return result

        def admit(self, proposals, review):
            ids = review.get("accepted_check_ids", []) if isinstance(review, dict) else []
            ids = ids if isinstance(ids, list) and all(isinstance(s, str) for s in ids) else []
            good = [c for c in proposals if c["id"] in ids]
            bad = [
                {"id": c["id"], "reason": "independent_review_not_admitted"}
                for c in proposals
                if c["id"] not in ids
            ]
            self.artifacts["checks"]["admitted"].extend(_V10V2_copy.deepcopy(good))
            self.artifacts["checks"]["rejected"].extend(bad)
            self.count("check_admitted", len(good))
            self.count("check_rejected", len(bad))

        def review(self, env, candidate, proposals, *, additions=False):
            instructions = (
                _V10V2_REVIEW_INSTRUCTIONS
                if additions
                else _V10V2_REVIEW_INSTRUCTIONS
                + "\nDo not add any additional checks in this review; return additional_checks: [].\n"
            )
            value = (
                self.json_call(
                    env,
                    instructions,
                    {
                        **self.context(),
                        "candidate": candidate["code"],
                        "proposed_checks": proposals,
                    },
                    "candidate_review",
                )
                or {}
            )
            clean = {
                "candidate_id": candidate["candidate_id"],
                "qa_hash": self.digest,
                "accepted_check_ids": value.get("accepted_check_ids", []),
                "issues": self.valid_issues(value.get("issues", [])),
                "unresolved": value.get("unresolved", []),
                "reason": value.get("reason", ""),
            }
            self.artifacts["reviews"].append(_V10V2_copy.deepcopy(clean))
            self.artifacts["checks"]["reviews"].append(_V10V2_copy.deepcopy(clean))
            if additions:
                self.admit(proposals, value)
                new = self.checks_from(
                    {"checks": value.get("additional_checks", [])},
                    limit=2,
                    existing_ids=[c["id"] for c in proposals],
                )
                if new:
                    audit = (
                        self.json_call(
                            env,
                            _V10V2_ADMISSION_INSTRUCTIONS,
                            {**self.context(), "proposed_checks": new},
                            "additional_check_admission",
                        )
                        or {}
                    )
                    self.artifacts["checks"]["reviews"].append(_V10V2_copy.deepcopy(audit))
                    self.admit(new, audit)
            return clean

        def execute_checks(self, env, candidate):
            checks = self.artifacts["checks"]["admitted"]
            if not checks:
                candidate["observations"] = []
                return []
            raw = env.exec_code(
                _V10V2_probe_script(candidate["code"], self.problem["entry_point"], checks)
            )
            rows = _V10V2_parse_observations(raw, checks)
            self.artifacts["probe_runs"].append(
                {
                    "candidate_id": candidate["candidate_id"],
                    "qa_hash": self.digest,
                    "raw": raw,
                    "observations": _V10V2_copy.deepcopy(rows),
                }
            )
            self.count("probe_runs")
            candidate["observations"] = rows
            return rows

        @staticmethod
        def passed(candidate, admitted):
            ids = {c["id"] for c in admitted}
            return {
                r["id"]
                for r in (candidate.get("observations") or [])
                if r["status"] == "pass" and r["id"] in ids
            }

        def challenge(self, env, ids):
            contested = [c for c in self.artifacts["checks"]["admitted"] if c["id"] in ids]
            if not contested:
                return False
            self.count("check_challenged", len(contested))
            audit = self.json_call(
                env,
                _V10V2_ADMISSION_INSTRUCTIONS,
                {**self.context(), "proposed_checks": contested},
                "contested_check_admission",
            )
            # An unavailable review is unknown, not permission to erase checks.
            if (
                not isinstance(audit, dict)
                or not isinstance(audit.get("accepted_check_ids"), list)
                or not all(isinstance(s, str) for s in audit["accepted_check_ids"])
            ):
                return False
            keep = set(audit["accepted_check_ids"])
            dropped = {c["id"] for c in contested if c["id"] not in keep}
            self.artifacts["checks"]["reviews"].append(_V10V2_copy.deepcopy(audit))
            if dropped:
                self.artifacts["checks"]["admitted"] = [
                    c for c in self.artifacts["checks"]["admitted"] if c["id"] not in dropped
                ]
                self.artifacts["checks"]["rejected"].extend(
                    {"id": ident, "reason": "contested_check_not_entailed"}
                    for ident in sorted(dropped)
                )
                self.count("check_rejected", len(dropped))
                # Recompute selection from the first eligible observed candidate:
                # erasing a check must not leave a former speculative winner ahead
                # on what is now a tie.
                self.best = None
                for candidate in self.artifacts["candidates"]:
                    if (
                        candidate["eligible"]
                        and candidate["qa_hash"] == self.digest
                        and candidate["observations"] is not None
                    ):
                        if self.best is None or self.passed(
                            self.best, self.artifacts["checks"]["admitted"]
                        ) < self.passed(candidate, self.artifacts["checks"]["admitted"]):
                            self.best = candidate
            return bool(dropped)

        def diagnosis(self, env, trigger, review):
            def schema(value):
                if (
                    value.get("action") not in {"repair", "challenge_checks", "stop"}
                    or not isinstance(value.get("diagnosis"), str)
                    or not isinstance(value.get("target"), str)
                ):
                    raise ValueError("diagnosis_schema_invalid")
                if not isinstance(value.get("challenged_check_ids"), list) or not all(
                    isinstance(s, str) for s in value["challenged_check_ids"]
                ):
                    raise ValueError("diagnosis_check_ids_invalid")
                if value["action"] != "stop":
                    _V10V2_validate_evidence(value.get("evidence"), self.problem, self.qa[1])
                return value

            value = self.json_call(
                env,
                _V10V2_DIAGNOSE_INSTRUCTIONS,
                {
                    **self.context(),
                    "trigger": trigger,
                    "candidate": self.best,
                    "admitted_checks_fallible": self.artifacts["checks"]["admitted"],
                    "review": review,
                },
                "failure_diagnosis",
                schema,
            )
            if value is not None:
                self.artifacts["diagnoses"].append(
                    {
                        "candidate_id": self.best["candidate_id"] if self.best else None,
                        "qa_hash": self.digest,
                        **_V10V2_copy.deepcopy(value),
                    }
                )
            return value

        def implement(self, env):
            self.brief(env)
            candidate = self.generate(env, {"kind": "initial_synthesis"})
            # A separately triggered structural-recovery slot is permitted, but the
            # pre-answer bridge is never a fallback for missing post-answer code.
            if (
                candidate is None
                and len(self.artifacts["candidates"]) < self.config["max_candidates"]
            ):
                self.count("repair_triggers")
                self.count("structural_recovery_triggers")
                candidate = self.generate(
                    env,
                    {
                        "kind": "structural_failure",
                        "previous_errors": self.artifacts["candidates"][-1]["format_errors"],
                    },
                )
                if candidate is not None:
                    self.count("repair_accepted")
                    candidate["selection_reason"] = "first_valid_current_qa_structural_recovery"
            if candidate is None:
                self.artifacts["status"] = "no_current_qa_valid_implementation"
                return
            self.best = candidate
            checks = self.json_call(
                env, _V10V2_CHECK_INSTRUCTIONS, self.context(), "visible_check_generation"
            )
            proposals = self.checks_from(checks, limit=4)
            review = self.review(env, candidate, proposals, additions=True)
            if self.execute_checks(env, candidate) is None:
                self.artifacts["status"] = "sandbox_observation_unknown_preserve_candidate"
                return
            seen_codes, seen_review_issues = {candidate["code"]}, set()
            for round_id in range(self.config["semantic_rounds"] + 1):
                admitted = self.artifacts["checks"]["admitted"]
                passed = self.passed(self.best, admitted)
                failures = [
                    r
                    for r in self.best["observations"]
                    if r["id"] in {c["id"] for c in admitted} and r["status"] != "pass"
                ]
                issues = [
                    i
                    for i in review["issues"]
                    if (self.best["code"], i["id"]) not in seen_review_issues
                ]
                self.artifacts["rounds"].append(
                    {
                        "round": round_id,
                        "candidate_id": self.best["candidate_id"],
                        "qa_hash": self.digest,
                        "admitted_check_ids": [c["id"] for c in admitted],
                        "passed_check_ids": sorted(passed),
                        "failures": _V10V2_copy.deepcopy(failures),
                        "issues": _V10V2_copy.deepcopy(issues),
                    }
                )
                if not failures and not issues:
                    self.artifacts["status"] = (
                        "visible_checks_satisfied"
                        if admitted
                        else "no_grounded_checks_preserve_candidate"
                    )
                    return
                if (
                    round_id == self.config["semantic_rounds"]
                    or len(self.artifacts["candidates"]) >= self.config["max_candidates"]
                ):
                    self.artifacts["status"] = "bounded_stop_preserve_visible_best"
                    return
                trigger = {
                    "kind": "credible_check_failure"
                    if failures
                    else "evidence_backed_review_defect",
                    "failures": _V10V2_copy.deepcopy(failures),
                    "issues": _V10V2_copy.deepcopy(issues),
                }
                self.count("repair_triggers")
                self.count("check_failure_triggers" if failures else "review_defect_triggers")
                diagnosed = self.diagnosis(env, trigger, review)
                if diagnosed is None or diagnosed["action"] == "stop":
                    self.artifacts["status"] = "diagnosis_stop_preserve_candidate"
                    return
                if diagnosed["action"] == "challenge_checks":
                    if not self.challenge(env, diagnosed["challenged_check_ids"]):
                        self.artifacts["status"] = "challenge_unconfirmed_preserve_candidate"
                        return
                    review = {**review, "issues": []}
                    continue
                # An unchanged candidate must not branch repeatedly on the same
                # review assertion. A newly accepted implementation may still have
                # that concrete defect, so issue identity is candidate-scoped.
                seen_review_issues.update((self.best["code"], i["id"]) for i in issues)
                revised = self.generate(env, trigger, diagnosed)
                if revised is None:
                    self.count("repair_rejected")
                    self.artifacts["status"] = "repair_structural_failure_preserve_candidate"
                    continue
                if revised["code"] in seen_codes:
                    revised["rejection_reason"] = "duplicate_code_no_progress"
                    self.count("repair_rejected")
                    self.artifacts["status"] = "no_progress_preserve_candidate"
                    return
                seen_codes.add(revised["code"])
                if self.execute_checks(env, revised) is None:
                    revised["rejection_reason"] = "sandbox_observation_unknown"
                    self.count("repair_rejected")
                    self.artifacts["status"] = "repair_observation_unknown_preserve_candidate"
                    return
                after_passed = self.passed(revised, admitted)
                if passed < after_passed:
                    self.best = revised
                    self.count("repair_accepted")
                    revised["selection_reason"] = "strict_check_improvement_without_regression"
                    review = self.review(env, revised, admitted)
                else:
                    revised["rejection_reason"] = (
                        "no_strict_improvement_or_previously_passed_check_regressed"
                    )
                    self.count("repair_rejected")
                    # Review assertions cannot break a check tie or undo an observed
                    # regression. The earliest retained program remains selected.
            self.artifacts["status"] = "bounded_stop_preserve_visible_best"

        def fallback(self):
            if self.best and self.best["eligible"] and self.best["qa_hash"] == self.digest:
                return self.best["code"]
            return (
                "def "
                + self.problem["entry_point"]
                + "(*args, **kwargs):\n    raise NotImplementedError\n"
            )

        def execute(self, env, fixed_qa=None):
            try:
                if fixed_qa is None:
                    self.plan_and_ask(env)
                else:
                    self.set_qa(*fixed_qa, status="conditioned_actual_qa")
                self.implement(env)
            except _V10V2_LimitsExceededException:
                self.artifacts["status"] = "official_limit_preserve_current_qa_candidate"
            code = self.fallback()
            self.artifacts.update(
                actual_question=self.qa[0],
                actual_answer=self.qa[1],
                qa_epoch=self.epoch,
                qa_hash=self.digest,
                selected_code=code,
            )
            self.artifacts["selection"] = {
                "candidate_id": self.best["candidate_id"] if self.best else None,
                "qa_hash": self.digest,
                "reason": self.best.get("selection_reason", "earliest_current_qa_valid_candidate")
                if self.best
                else "no_valid_current_qa_candidate_explicit_stub",
                "code_sha256": _V10V2_hashlib.sha256(code.encode("utf-8")).hexdigest(),
                "uses_hidden_scores": False,
                "ties_retain_first": True,
            }
            self.artifacts["mechanisms"]["check_admitted_final"] = len(
                self.artifacts["checks"]["admitted"]
            )
            self.artifacts["mechanisms"]["candidate_rejected_total"] = sum(
                bool(c.get("rejection_reason")) for c in self.artifacts["candidates"]
            )
            return code

        initialize = __init__

    class _V10V2_IntentBridgeV2Clarifier(_V10V2_ClarificationAlgorithmBase):
        DEFAULT_CONFIG = {"repair_attempts": 1, "semantic_rounds": 2, "max_candidates": 3}

        def __init__(self, config=None, *, policy=None):
            _IBInitializeConfig(self, config=config)
            self.policy = _V10V2_validate_policy(_V10V2_BASE_POLICY if policy is None else policy)

        def localRun(self, env, problem, fixed_qa=None):
            for field, ceiling in self.DEFAULT_CONFIG.items():
                if type(self.config[field]) is not int or not 0 <= self.config[field] <= ceiling:
                    raise ValueError(field + " must be an integer within the fixed default ceiling")
            if self.config["max_candidates"] < 1:
                raise ValueError("max_candidates must allow the initial implementation")
            visible = {"prompt": problem["prompt"], "entry_point": problem["entry_point"]}
            if (
                not isinstance(visible["prompt"], str)
                or not isinstance(visible["entry_point"], str)
                or not visible["entry_point"].isidentifier()
                or _V10V2_keyword.iskeyword(visible["entry_point"])
            ):
                raise ValueError("invalid_visible_task_or_entry_point")
            state = _V10V2__Run(
                dict(self.config),
                _V10V2_copy.deepcopy(self.policy),
                visible,
                conditioned=fixed_qa is not None,
            )
            try:
                return state.execute(env, fixed_qa)
            finally:
                self.artifacts, self.trace = (
                    _V10V2_copy.deepcopy(state.artifacts),
                    _V10V2_copy.deepcopy(state.trace),
                )

        def run(self, env, problem):
            return self.localRun(env, problem)

        def run_conditioned(self, env, problem, question, answer):
            # fmt: off
            """Coding-only diagnostic with externally preserved real TRAIN Q/A.

        The caller owns Q/A provenance. No question is asked and no environment
        history is synthesized; results must not be called end-to-end scores.
        """
            # fmt: on
            if not isinstance(question, str) or not isinstance(answer, str):
                raise TypeError("conditioned_actual_qa_must_be_strings")
            return self.localRun(env, problem, (question, answer))

        initialize = __init__

    # Frozen source: pilot/intentbridge_v3_20261101/checks.py
    """Candidate-blind visible-check guards and v2-compatible probe extensions.

The syntax guard is deliberately incomplete: an unparsed natural-language
keyword contract is an unknown proposed check, not a prohibition on the task's
interface. Independent visible-evidence admission must still review invocation,
domain, value, type, channel and formatting. No candidate signature is read.
"""

    import ast as _V10Checks_ast
    import copy as _V10Checks_copy
    import io as _V10Checks_io
    import re as _V10Checks_re
    import tokenize as _V10Checks_tokenize

    _V10Checks_CHECK_SCHEMA = """Retain the v2 CHECK schema and fully typed nested values.
Additional properties are {name:'truthiness',expected:true|false} for Python
truthiness of the return value (this does NOT require a bool return), and
{name:'stdout_content',expected:TYPED_STRING} for stdout equal to that exact
content with zero or one additional terminal LF. All content characters,
including whitespace, internal LF and literal backslashes, remain significant.
Use exact target:'stdout' only when its entire formatting, including final
newline presence/absence, is evidenced. These properties impose no other
return type or return value. length_equals_input needs a sized decoded input.
"""

    _V10Checks_CHECK_SEMANTICS_INSTRUCTIONS = (
        """Review every proposed invocation, domain,
value/property, type, output channel and formatting separately against the full
visible prompt and literal real answer. None has a fixed priority. Unknown
stays unknown; do not force a check into executable form. A candidate signature
is not interface evidence: a visibly legal call that fails to bind may expose a
candidate bug. Conversely, never inject a keyword just because a candidate can
accept it. Prefer a grounded positional call when keyword naming is unknown.
Exact visible Python signatures/calls provide mechanical keyword provenance;
unparsed natural-language-only keyword contracts remain unknown to that guard.
Do not automatically drop, reorder, fill, flatten, unwrap or unescape arguments,
change their types, add an adapter, or repair a candidate to fit an invalid check.
Printed content does not by itself specify exact terminal newline behavior;
truthiness does not by itself require an exact bool. Exact type claims and
numeric_value, truthiness, stdout_content all need their own visible support.
"""
        + _V10Checks_CHECK_SCHEMA
    )

    def _V10Checks__typed_equal(left, right):
        """Literal comparison that does not collapse bool/int or nested types."""
        if type(left) is not type(right):
            return False
        if type(left) in {tuple, list}:
            return len(left) == len(right) and all(
                _V10Checks__typed_equal(a, b) for a, b in zip(left, right, strict=False)
            )
        if type(left) is dict:
            return len(left) == len(right) and all(
                any(
                    _V10Checks__typed_equal(k, other) and _V10Checks__typed_equal(v, right[other])
                    for other in right
                )
                for k, v in left.items()
            )
        return left == right

    def _V10Checks__literal_data_ranges(text):
        # fmt: off
        """Find established string/comment payloads without parsing prose as code.

    Whole-source tokenization handles multiline literals. Per-line passes keep
    later lines protected if unrelated prose indentation truncates that pass.
    A call/signature spelled inside such data is not interface provenance.
    This conservative guard may omit docstring-only keyword examples; it never
    changes the candidate interface or claims the unknown invocation illegal.
    """
        # fmt: on
        lines = text.splitlines(keepends=True)
        offsets, total = [], 0
        for line in lines:
            offsets.append(total)
            total += len(line)
        offsets.append(total)
        excluded = set()

        def collect(fragment, base):
            fragment_lines = fragment.splitlines(keepends=True)
            fragment_offsets, count = [], 0
            for line in fragment_lines:
                fragment_offsets.append(count)
                count += len(line)
            fragment_offsets.append(count)
            stream = _V10Checks_tokenize.generate_tokens(_V10Checks_io.StringIO(fragment).readline)
            fstrings = []
            fstring_start = getattr(_V10Checks_tokenize, "FSTRING_START", None)
            fstring_end = getattr(_V10Checks_tokenize, "FSTRING_END", None)

            def offset(position, *, one_based_column=False):
                row, column = position
                column = max(0, column - int(one_based_column))
                return fragment_offsets[min(max(0, row - 1), len(fragment_offsets) - 1)] + column

            def unfinished(start, spelling):
                # A malformed single-line literal makes the rest of that physical
                # line uncertain; a triple-quoted literal can extend to EOF.
                triple = _V10Checks_re.match(r"(?i)^[frbu]*(?:'''|\"\"\")", spelling) is not None
                newline = fragment.find("\n", start)
                end = count if triple or newline < 0 else newline + 1
                excluded.add((base + start, base + end))

            try:
                for token in stream:
                    if token.type == fstring_start:
                        fstrings.append((offset(token.start), token.string))
                        continue
                    if token.type == fstring_end:
                        if fstrings:
                            start, _ = fstrings.pop()
                            excluded.add((base + start, base + offset(token.end)))
                        continue
                    if token.type == _V10Checks_tokenize.ERRORTOKEN and token.string in {"'", '"'}:
                        unfinished(offset(token.start), token.string)
                    if token.type not in {_V10Checks_tokenize.STRING, _V10Checks_tokenize.COMMENT}:
                        continue
                    start = base + offset(token.start)
                    end = base + offset(token.end)
                    excluded.add((start, end))
            except (_V10Checks_tokenize.TokenError, IndentationError, SyntaxError) as error:
                # CPython versions can report an unfinished ordinary string before
                # yielding its STRING/ERRORTOKEN. Preserve that known uncertainty.
                if (
                    isinstance(error, _V10Checks_tokenize.TokenError)
                    and len(error.args) > 1
                    and "string" in str(error.args[0]).lower()
                    and isinstance(error.args[1], tuple)
                    and len(error.args[1]) == 2
                ):
                    start = offset(error.args[1], one_based_column=True)
                    unfinished(start, fragment[start:])
            finally:
                for start, spelling in fstrings:
                    unfinished(start, spelling)

        collect(text, 0)
        for offset, line in zip(offsets, lines, strict=False):
            collect(line, offset)
        return sorted(excluded)

    def _V10Checks__within_literal(position, excluded):
        return any(start <= position < end for start, end in excluded)

    def _V10Checks__visible_signatures(text, entry_point, excluded=()):
        """Read only literal Python definition headers; never execute annotations."""
        pattern = (
            r"(?<![\w.])(?:async[ \t]+)?def[ \t]+" + _V10Checks_re.escape(entry_point) + r"[ \t]*\("
        )
        for match in _V10Checks_re.finditer(pattern, text):
            if _V10Checks__within_literal(match.start(), excluded):
                continue
            suffix = text[match.start() :]
            # The first complete parsed header ends at the function-header colon.
            # Colons inside annotations/defaults will not form a valid definition.
            # Keeping just the header also handles one-line bodies and backticks.
            for position, character in enumerate(suffix):
                if character != ":":
                    continue
                candidate = suffix[: position + 1]
                try:
                    tree = _V10Checks_ast.parse(candidate + "\n    pass\n")
                except (SyntaxError, ValueError):
                    continue
                if len(tree.body) == 1 and isinstance(
                    tree.body[0], (_V10Checks_ast.FunctionDef, _V10Checks_ast.AsyncFunctionDef)
                ):
                    node = tree.body[0]
                    if node.name == entry_point:
                        yield candidate, node.args
                break

    def _V10Checks__visible_calls(text, entry_point, excluded=()):
        """Parse literal call spans in code, doctests, backticks or surrounding prose."""
        pattern = r"(?<![\w.])" + _V10Checks_re.escape(entry_point) + r"\s*\("
        for match in _V10Checks_re.finditer(pattern, text):
            if _V10Checks__within_literal(match.start(), excluded):
                continue
            suffix = text[match.start() :]
            for position, character in enumerate(suffix):
                if character != ")":
                    continue
                quote = suffix[: position + 1]
                try:
                    node = _V10Checks_ast.parse(quote, mode="eval").body
                except (SyntaxError, ValueError):
                    continue
                if (
                    isinstance(node, _V10Checks_ast.Call)
                    and isinstance(node.func, _V10Checks_ast.Name)
                    and node.func.id == entry_point
                ):
                    yield quote, node
                    break

    def _V10Checks_invocation_provenance(check, problem, answer):
        # fmt: off
        """Return syntactic keyword support and literal-call matches from visible data.

    Support proves only the syntax observed here. It does not prove domain,
    current answer scope, expected result or semantic legality. Positional
    arguments and candidate signatures are never rewritten or used as authority.
    """
        # fmt: on
        requested = set(check["kwargs"])
        support = {name: [] for name in requested}
        literal_matches = []
        args = [_V10V2_decode_typed(item) for item in check["args"]]
        kwargs = {name: _V10V2_decode_typed(item) for name, item in check["kwargs"].items()}
        for source, text in (("prompt", problem["prompt"]), ("actual_answer", answer)):
            excluded = _V10Checks__literal_data_ranges(text)
            for quote, arguments in _V10Checks__visible_signatures(
                text, problem["entry_point"], excluded
            ):
                names = {item.arg for item in [*arguments.args, *arguments.kwonlyargs]}
                for name in requested:
                    if name in names or arguments.kwarg is not None:
                        support[name].append(
                            {"source": source, "quote": quote, "basis": "visible_signature"}
                        )
            for quote, node in _V10Checks__visible_calls(text, problem["entry_point"], excluded):
                for keyword in node.keywords:
                    if keyword.arg in requested:
                        support[keyword.arg].append(
                            {"source": source, "quote": quote, "basis": "visible_call"}
                        )
                try:
                    if any(isinstance(item, _V10Checks_ast.Starred) for item in node.args) or any(
                        item.arg is None for item in node.keywords
                    ):
                        continue
                    visible_args = [_V10Checks_ast.literal_eval(item) for item in node.args]
                    visible_kwargs = {
                        item.arg: _V10Checks_ast.literal_eval(item.value) for item in node.keywords
                    }
                except (TypeError, ValueError, SyntaxError, RecursionError):
                    continue
                if _V10Checks__typed_equal(args, visible_args) and _V10Checks__typed_equal(
                    kwargs, visible_kwargs
                ):
                    literal_matches.append(
                        {"source": source, "quote": quote, "basis": "exact_literal_call"}
                    )
        return {
            "keywords": {
                name: {"status": "supported" if quotes else "unknown", "evidence": quotes}
                for name, quotes in sorted(support.items())
            },
            "literal_call_matches": literal_matches,
            "candidate_signature_used": False,
        }

    def _V10Checks__reference(check, ref):
        item = check["args"][ref["arg"]] if "arg" in ref else check["kwargs"][ref["kwarg"]]
        return _V10V2_decode_typed(item)

    def _V10Checks_validate_checks(
        value, problem, answer, *, existing_ids=(), limit=_V10V2_MAX_CHECKS
    ):
        """Use v2 typed/evidence gates plus conservative invocation/property guards."""
        if not isinstance(value, dict) or not isinstance(value.get("checks"), list):
            raise ValueError("checks_array_required")
        good, rejected, used = [], [], set(existing_ids)
        for position, check in enumerate(value["checks"]):
            ident = check.get("id", "") if isinstance(check, dict) else ""
            try:
                if position >= limit:
                    raise ValueError("check_limit_exceeded")
                projected = _V10Checks_copy.deepcopy(check)
                prop = check.get("property", {}) if isinstance(check, dict) else {}
                name = prop.get("name") if isinstance(prop, dict) else None
                if name == "truthiness":
                    if set(prop) != {"name", "expected"} or type(prop["expected"]) is not bool:
                        raise ValueError("truthiness_property_requires_boolean_expectation")
                    projected["property"] = {"name": "nonmutation"}
                elif name == "stdout_content":
                    if (
                        set(prop) != {"name", "expected"}
                        or type(_V10V2_decode_typed(prop["expected"])) is not str
                    ):
                        raise ValueError("stdout_content_requires_typed_string")
                    projected["property"] = {"name": "nonmutation"}
                base_good, base_bad = _V10V2_validate_checks(
                    {"checks": [projected]}, problem, answer, existing_ids=used, limit=1
                )
                if not base_good:
                    raise ValueError(base_bad[0]["reason"])
                if name == "length_equals_input":
                    try:
                        len(_V10Checks__reference(check, prop["input"]))
                    except TypeError:
                        raise ValueError("length_equals_input_requires_sized_input") from None
                provenance = _V10Checks_invocation_provenance(check, problem, answer)
                unknown = [
                    name
                    for name, result in provenance["keywords"].items()
                    if result["status"] == "unknown"
                ]
                if unknown:
                    raise ValueError("keyword_invocation_not_visibly_grounded:" + ",".join(unknown))
            except (AttributeError, KeyError, TypeError, ValueError, RecursionError) as error:
                rejected.append({"id": ident, "reason": str(error)})
                continue
            good.append(_V10Checks_copy.deepcopy(check))
            used.add(ident)
        return good, rejected

    def _V10Checks_extension_property_satisfied(prop, actual, stdout):
        """Pure semantics shared by synthetic regressions; no program is executed."""
        if prop["name"] == "truthiness":
            if type(prop.get("expected")) is not bool or set(prop) != {"name", "expected"}:
                raise ValueError("truthiness_property_requires_boolean_expectation")
            return bool(actual) is prop["expected"]
        if prop["name"] == "stdout_content":
            expected = _V10V2_decode_typed(prop["expected"])
            if (
                type(expected) is not str
                or type(stdout) is not str
                or set(prop) != {"name", "expected"}
            ):
                raise ValueError("stdout_content_requires_typed_string")
            return stdout == expected or stdout == expected + "\n"
        raise ValueError("unsupported_extension_property")

    def _V10Checks_probe_script(code, entry_point, checks):
        """Generate a v2 observation protocol script for environment-only execution."""
        cases = _V10Checks_copy.deepcopy(checks)
        for check in cases:
            if check.get("kind") == "property" and check["property"]["name"] == "stdout_content":
                check["property"]["expected"] = _V10V2_decode_typed(check["property"]["expected"])
        script = _V10V2_probe_script(code, entry_point, cases)
        anchor = "            elif _ib_name == 'numeric_value':\n"
        if script.count(anchor) != 1:
            raise ValueError("v2_probe_extension_anchor_changed")
        branches = """            elif _ib_name == 'truthiness':
                _ib_ok = bool(_ib_actual) is _ib_prop['expected']
            elif _ib_name == 'stdout_content':
                _ib_expected = _ib_prop['expected']
                _ib_ok = _ib_stdout == _ib_expected or _ib_stdout == _ib_expected + '\\n'
"""
        return script.replace(anchor, branches + anchor, 1)

    # Frozen source: pilot/intentbridge_v3_20261101/evidence.py
    """Literal visible-text evidence and independently validated brief facts.

This module does not execute candidate programs, read tasks from disk, or infer
semantic entailment.  A valid citation establishes only that the quoted text is
present in the current visible source.  Complete prompt and actual Q/A remain
the authority even when every structured fact is rejected.
"""

    import copy as _V10Evidence_copy
    import hashlib as _V10Evidence_hashlib
    import json as _V10Evidence_json
    import re as _V10Evidence_re

    _V10Evidence_SOURCES = ("prompt", "actual_answer")
    _V10Evidence_BRIEF_FIELDS = ("confirmed", "scope_updates", "unresolved")
    _V10Evidence_CATALOG_VERSION = 1
    _V10Evidence_SPAN_CHARS = 480

    class EvidenceValidationError(ValueError):
        """A mechanical evidence rejection with machine-readable field paths."""

        def __init__(self, errors):
            self.errors = _V10Evidence_copy.deepcopy(errors)
            _IBInitializeException(
                self, "; ".join(e["path"] + ": " + e["code"] for e in self.errors)
            )

        initialize = __init__

    def _V10Evidence__error(path, code):
        return {"path": path, "code": code}

    def _V10Evidence__sha(value):
        return _V10Evidence_hashlib.sha256(
            value.encode("utf-8", errors="surrogatepass")
        ).hexdigest()

    def _V10Evidence__authority(problem, answer, question):
        # Deliberately access only the two allowed visible problem fields.
        prompt, entry_point = problem["prompt"], problem["entry_point"]
        if not all(isinstance(s, str) for s in (prompt, entry_point, question, answer)):
            raise TypeError("visible_prompt_entry_point_and_actual_qa_must_be_strings")
        return {
            "prompt": prompt,
            "entry_point": entry_point,
            "actual_question": question,
            "actual_answer": answer,
        }

    def _V10Evidence__context_hash(authority):
        return _V10Evidence__sha(
            _V10Evidence_json.dumps(
                authority, ensure_ascii=True, sort_keys=True, separators=(",", ":")
            )
        )

    def _V10Evidence__same_json(left, right):
        # Python equality alone considers True == 1 and 1.0 == 1.  Catalog offsets,
        # lengths and versions must retain their exact JSON types as well as values.
        try:
            return _V10Evidence_json.dumps(
                left, ensure_ascii=True, sort_keys=True, allow_nan=False, separators=(",", ":")
            ) == _V10Evidence_json.dumps(
                right, ensure_ascii=True, sort_keys=True, allow_nan=False, separators=(",", ":")
            )
        except (TypeError, ValueError):
            return False

    def _V10Evidence_build_evidence_catalog(problem, answer, *, question=""):
        # fmt: off
        """Return deterministic literal line/chunk spans for this exact visible Q/A.

    Offsets index Python Unicode code points, with an exclusive ``end``.  Line
    endings, spaces and literal backslashes are retained.  Empty/whitespace-only
    pieces are omitted; an empty actual answer therefore supplies no evidence.
    IDs bind prompt, entry point and the entire actual Q/A, not task identities.
    """
        # fmt: on
        authority = _V10Evidence__authority(problem, answer, question)
        context = _V10Evidence__context_hash(authority)
        result = {
            "version": _V10Evidence_CATALOG_VERSION,
            "context_sha256": context,
            "offset_unit": "python_unicode_codepoint",
            "sources": {},
            "spans": [],
        }
        for source in _V10Evidence_SOURCES:
            text = authority[source]
            result["sources"][source] = {"sha256": _V10Evidence__sha(text), "length": len(text)}
            line_start = 0
            for line in text.splitlines(keepends=True):
                for relative in range(0, len(line), _V10Evidence_SPAN_CHARS):
                    start = line_start + relative
                    end = min(line_start + len(line), start + _V10Evidence_SPAN_CHARS)
                    quote = text[start:end]
                    if quote.strip():
                        binding = _V10Evidence_json.dumps(
                            [
                                _V10Evidence_CATALOG_VERSION,
                                context,
                                source,
                                start,
                                end,
                                _V10Evidence__sha(quote),
                            ],
                            separators=(",", ":"),
                        )
                        result["spans"].append(
                            {
                                "source": source,
                                "span_id": "ev_" + _V10Evidence__sha(binding),
                                "start": start,
                                "end": end,
                                "quote": quote,
                            }
                        )
                line_start += len(line)
        return result

    def _V10Evidence__checked_catalog(problem, answer, question, catalog):
        expected = _V10Evidence_build_evidence_catalog(problem, answer, question=question)
        if catalog is None:
            return expected
        if not isinstance(catalog, dict):
            code = "evidence_catalog_invalid"
        elif catalog.get("context_sha256") != expected["context_sha256"]:
            code = "evidence_catalog_context_mismatch"
        elif not _V10Evidence__same_json(catalog.get("sources"), expected["sources"]):
            code = "evidence_catalog_source_mismatch"
        elif not _V10Evidence__same_json(catalog, expected):
            code = "evidence_catalog_tampered"
        else:
            return expected
        raise EvidenceValidationError([_V10Evidence__error("evidence_catalog", code)])

    def _V10Evidence_resolve_evidence(
        value, problem, answer, *, answer_required=False, catalog=None, question="", path="evidence"
    ):
        # fmt: off
        """Resolve old literal quotes or current span IDs to canonical exact quotes.

    ``{source, quote}`` and ``{source, span_id}`` are the only input forms.  No
    fuzzy matching, whitespace normalization, escape decoding, source guessing
    or caller-supplied offset slicing is performed.  A provided catalog is
    regenerated and compared before use, so mutable metadata is not authority.
    """
        # fmt: on
        current = _V10Evidence__checked_catalog(problem, answer, question, catalog)
        authority = _V10Evidence__authority(problem, answer, question)
        if not isinstance(value, list) or not value:
            raise EvidenceValidationError([_V10Evidence__error(path, "source_evidence_required")])
        spans = {item["span_id"]: item for item in current["spans"]}
        good, errors = [], []
        for index, item in enumerate(value):
            item_path = path + "[" + str(index) + "]"
            if not isinstance(item, dict) or set(item) not in (
                {"source", "quote"},
                {"source", "span_id"},
            ):
                errors.append(_V10Evidence__error(item_path, "invalid_evidence_object"))
                continue
            source = item["source"]
            if not isinstance(source, str) or source not in _V10Evidence_SOURCES:
                errors.append(_V10Evidence__error(item_path + ".source", "invalid_evidence_source"))
                continue
            if "span_id" in item:
                ident = item["span_id"]
                if not isinstance(ident, str) or ident not in spans:
                    errors.append(
                        _V10Evidence__error(
                            item_path + ".span_id", "evidence_span_unknown_or_stale"
                        )
                    )
                    continue
                span = spans[ident]
                if span["source"] != source:
                    errors.append(
                        _V10Evidence__error(item_path + ".source", "evidence_span_source_mismatch")
                    )
                    continue
                quote = span["quote"]
            else:
                quote = item["quote"]
            if not isinstance(quote, str) or not quote.strip() or quote not in authority[source]:
                errors.append(_V10Evidence__error(item_path + ".quote", "evidence_quote_not_exact"))
                continue
            good.append({"source": source, "quote": quote})
        if answer_required and not any(item["source"] == "actual_answer" for item in good):
            errors.append(_V10Evidence__error(path, "scope_update_requires_actual_answer_evidence"))
        if errors:
            raise EvidenceValidationError(errors)
        return good

    # Convenient drop-in name for callers replacing the v2 strict quote validator.
    _V10Evidence_validate_evidence = _V10Evidence_resolve_evidence

    def _V10Evidence_validate_brief_partial(value, problem, answer, *, catalog=None, question=""):
        # fmt: off
        """Keep independently valid facts and unknowns, with precise local errors.

    Every evidence item in a fact must pass.  A valid neighboring citation does
    not rescue a fact with a bad citation, and invalid facts are never moved to
    ``confirmed``.  ``raw_brief`` exists solely to retain repair slot positions;
    only ``brief`` contains mechanically accepted facts.  Neither is a semantic
    proof.  The complete raw authority is returned without rewriting it.
    """
        # fmt: on
        authority = _V10Evidence__authority(problem, answer, question)
        result = {
            "brief": {field: [] for field in _V10Evidence_BRIEF_FIELDS},
            "errors": [],
            "valid_paths": [],
            "context_sha256": _V10Evidence__context_hash(authority),
            "authority": authority,
            "raw_brief": _V10Evidence_copy.deepcopy(value),
        }
        errors = result["errors"]
        if not isinstance(value, dict):
            errors.append(_V10Evidence__error("$", "brief_object_required"))
            return result
        if set(value) - set(_V10Evidence_BRIEF_FIELDS):
            errors.append(_V10Evidence__error("$", "brief_unexpected_fields"))
        for field in _V10Evidence_BRIEF_FIELDS:
            if field not in value:
                errors.append(_V10Evidence__error(field, "brief_field_missing"))
                continue
            if not isinstance(value[field], list):
                errors.append(_V10Evidence__error(field, "brief_array_required"))
                continue
            for index, item in enumerate(value[field]):
                item_path = field + "[" + str(index) + "]"
                if field == "unresolved":
                    if not isinstance(item, str):
                        errors.append(
                            _V10Evidence__error(item_path, "brief_unknown_must_be_string")
                        )
                        continue
                    result["brief"][field].append(item)
                    result["valid_paths"].append(item_path)
                    continue
                if not isinstance(item, dict):
                    errors.append(_V10Evidence__error(item_path, "brief_fact_object_required"))
                    continue
                before = len(errors)
                if set(item) != {"fact", "evidence"}:
                    errors.append(_V10Evidence__error(item_path, "brief_fact_fields_invalid"))
                if not isinstance(item.get("fact"), str) or not item["fact"].strip():
                    errors.append(
                        _V10Evidence__error(item_path + ".fact", "brief_fact_text_required")
                    )
                canonical = None
                try:
                    canonical = _V10Evidence_resolve_evidence(
                        item.get("evidence"),
                        problem,
                        answer,
                        answer_required=field == "scope_updates",
                        catalog=catalog,
                        question=question,
                        path=item_path + ".evidence",
                    )
                except EvidenceValidationError as error:
                    errors.extend(error.errors)
                if before == len(errors):
                    result["brief"][field].append({"fact": item["fact"], "evidence": canonical})
                    result["valid_paths"].append(item_path)
        return result

    def _V10Evidence_merge_brief_repair(
        previous, repaired_value, problem, answer, *, repair_paths=None, catalog=None, question=""
    ):
        # fmt: off
        """Apply a targeted response, then revalidate under the current authority.

    A response uses the same three brief fields and original item positions.
    With ``repair_paths=None``, every explicitly supplied field replaces that
    complete field.  Otherwise paths name fields or fact/unknown slots; deeper
    paths target their enclosing slot, and ``$`` replaces the whole object.
    Any scope update repair replaces the
    *entire* scope_updates field, including an empty replacement.  Scope updates
    are never unioned because that can retain superseded statements.  Semantic
    contradictions still require review against the full literal authority.

    Retention uses only previously validated slots, never arbitrary raw prior
    facts.  Previous state from different visible Q/A is discarded, even if its
    quoted fragment happens to occur again in the new task.
    """
        # fmt: on
        authority = _V10Evidence__authority(problem, answer, question)
        current_hash = _V10Evidence__context_hash(authority)
        errors = []
        base = {field: [] for field in _V10Evidence_BRIEF_FIELDS}
        same_context = (
            isinstance(previous, dict)
            and previous.get("context_sha256") == current_hash
            and previous.get("authority") == authority
        )
        if same_context:
            # Revalidate raw slots instead of trusting caller-mutated brief data or
            # valid_paths.  Rejected prior slots are holes, not confirmed facts.
            prior = _V10Evidence_validate_brief_partial(
                previous.get("raw_brief"), problem, answer, catalog=catalog, question=question
            )
            raw = prior["raw_brief"]
            if isinstance(raw, dict):
                valid = set(prior["valid_paths"])
                for field in _V10Evidence_BRIEF_FIELDS:
                    items = raw.get(field)
                    if isinstance(items, list):
                        base[field] = [
                            _V10Evidence_copy.deepcopy(item)
                            if field + "[" + str(i) + "]" in valid
                            else None
                            for i, item in enumerate(items)
                        ]
        else:
            errors.append(
                _V10Evidence__error("previous.context_sha256", "brief_repair_context_mismatch")
            )

        if not isinstance(repaired_value, dict):
            checked = _V10Evidence_validate_brief_partial(
                base, problem, answer, catalog=catalog, question=question
            )
            checked["errors"] = (
                errors
                + [_V10Evidence__error("$", "brief_repair_object_required")]
                + checked["errors"]
            )
            return checked
        if set(repaired_value) - set(_V10Evidence_BRIEF_FIELDS):
            errors.append(_V10Evidence__error("$", "brief_repair_unexpected_fields"))
        targets = list(repaired_value) if repair_paths is None else repair_paths
        if not isinstance(targets, (list, tuple)):
            errors.append(_V10Evidence__error("repair_paths", "brief_repair_paths_invalid"))
            targets = []
        replacements = set()
        for path in targets:
            if not isinstance(path, str):
                errors.append(_V10Evidence__error("repair_paths", "brief_repair_path_invalid"))
                continue
            if path == "$":
                base = {
                    field: _V10Evidence_copy.deepcopy(repaired_value.get(field))
                    for field in _V10Evidence_BRIEF_FIELDS
                }
                replacements.update(_V10Evidence_BRIEF_FIELDS)
                continue
            match = _V10Evidence_re.fullmatch(
                r"(confirmed|scope_updates|unresolved)(?:\[(0|[1-9][0-9]*)\](?:\..+)?)?", path
            )
            if match is None:
                errors.append(_V10Evidence__error(path, "brief_repair_path_invalid"))
                continue
            field, index = match.groups()
            # A requested scope replacement invalidates all old scoped statements,
            # even when the replacement is malformed or absent.
            if index is None or field == "scope_updates":
                if field not in replacements:
                    base[field] = _V10Evidence_copy.deepcopy(repaired_value.get(field))
                    replacements.add(field)
                continue
            if field in replacements:
                continue
            index = int(index)
            items = repaired_value.get(field)
            if not isinstance(items, list) or index >= len(items):
                errors.append(
                    _V10Evidence__error(field + "[" + str(index) + "]", "brief_repair_slot_missing")
                )
                if index < len(base[field]):
                    base[field][index] = None
                continue
            # Avoid unbounded allocation from a fabricated repair index.  A new
            # slot can only be taken from an actual response array of that length.
            while len(base[field]) <= index:
                base[field].append(None)
            base[field][index] = _V10Evidence_copy.deepcopy(items[index])
        checked = _V10Evidence_validate_brief_partial(
            base, problem, answer, catalog=catalog, question=question
        )
        checked["errors"] = errors + checked["errors"]
        return checked

    # Frozen source: pilot/intentbridge_v3_20261101/review.py
    """Visible-evidence review routing and candidate-blind check reassessment.

These are schema/provenance guards, not a semantic entailment oracle.  A model's
grounding claim remains fallible; a candidate issue cannot select a program.
Selection still requires strict nonregressing improvement on admitted checks.
"""

    import copy as _V10Review_copy

    _V10Review_FACETS = ("invocation", "domain", "value", "type", "channel", "format")
    _V10Review_VISIBLE_BASIS = "visible_requirement"
    _V10Review_BLIND_DERIVATION = (
        "Independently recompute this check from the quoted visible evidence."
    )
    _V10Review_OBJECTION_REASONS = {
        "unsupported_invocation": "Reassess whether the check's invocation follows from the quoted visible evidence.",
        "unsupported_domain": "Reassess whether the check's input domain follows from the quoted visible evidence.",
        "unsupported_value": "Reassess whether the check's expected value or property follows from the quoted visible evidence.",
        "unsupported_type": "Reassess whether the check's type assertions follow from the quoted visible evidence.",
        "unsupported_channel": "Reassess whether the check's output channel follows from the quoted visible evidence.",
        "unsupported_format": "Reassess whether the check's formatting assertions follow from the quoted visible evidence.",
        "stale_scope": "Reassess whether the check remains supported after the quoted visible answer.",
        "property_domain": "Reassess whether the property is defined on the input domain under the quoted visible evidence.",
    }

    _V10Review_REVIEW_INSTRUCTIONS = """Review candidate defects separately from check defects.
Return issues as {id:string,subject:'candidate'|'check',defect:string,
basis:'visible_requirement',evidence:[{source:'prompt'|'actual_answer',quote:string}],
check_ids:[string],facets:[FACET]}. FACET is invocation/domain/value/type/channel/
format. Use exact visible quotes and explain a concrete defect. For a check
objection identify the currently admitted check IDs and affected facets. An
opinion, confidence, candidate output, or model agreement is not requirement
evidence. Check defects must never be sent to code repair as candidate defects.
Candidate issues may request diagnosis but cannot select a replacement program.
"""

    _V10Review_FACET_INSTRUCTIONS = """Independently assess proposed checks using only the
complete visible task, entry_point and literal actual Q/A. The objection is
fallible and is not evidence. Do not infer requirements from any implementation
or execution. Return {check_assessments:[{id:string,facets:{invocation:FACET,
domain:FACET,value:FACET,type:FACET,channel:FACET,format:FACET}}],reason:string}.
Each FACET is {known:true|false,verdict:'supported'|'contradicted'|'unknown',
reason:string,evidence:[{source:'prompt'|'actual_answer',quote:string}]}.
For known:true, verdict may be omitted or 'supported'. For known:false, verdict
MUST distinguish 'contradicted' (a concrete visible-evidence contradiction) from
'unknown' (insufficient evidence or uncertainty). Unknown may use evidence:[].
Return all six facet objects. Admit only when all SIX facets are known true
and follow from exact visible evidence. Missing, unknown or 'irrelevant' is not
true. Invocation includes argument count/order/keywords/container nesting;
domain includes legal inputs; value means the stated value OR PROPERTY follows
from the evidence; type includes each asserted type distinction; channel
distinguishes return/stdout; format includes only the precision or formatting
actually asserted. A property still needs its value facet justified. A numeric
value check can justify not asserting int versus float; a check that asserts no
formatting constraint can explain that fact. Do not invent unsupported facets.
Bare accepted_check_ids cannot substitute for these assessments.
During a challenge of an already-admitted check, malformed/missing/unknown
assessments do not revoke it. Only an explicit known:false, verdict:'contradicted'
facet with exact visible evidence and a reason can conclusively reject a check.
"""

    _V10Review_DIAGNOSIS_INSTRUCTIONS = """For action challenge_checks, supply check_objections:
[{check_ids:[string],objection_kind:'unsupported_invocation'|'unsupported_domain'|
'unsupported_value'|'unsupported_type'|'unsupported_channel'|'unsupported_format'|
'stale_scope'|'property_domain',basis:'visible_requirement',
evidence:[{source:'prompt'|'actual_answer',quote:string}],facets:[FACET]}].
These objections are shown to a candidate-blind reviewer using only canonical
objection labels, exact visible evidence and selected facets. No free reason,
defect or diagnosis prose is forwarded. Do not quote or describe candidate code,
candidate outputs, exceptions, execution, probes, or observations in the objection.
Keep any execution discussion only in the separate diagnosis field.
"""

    def _V10Review__evidence(value, problem, answer):
        if not isinstance(value, list) or not value:
            raise ValueError("source_evidence_required")
        clean = []
        for item in value:
            if not isinstance(item, dict) or set(item) != {"source", "quote"}:
                raise ValueError("invalid_evidence_object")
            source = item["source"]
            if source not in {"prompt", "actual_answer"}:
                raise ValueError("invalid_evidence_source")
            text = problem["prompt"] if source == "prompt" else answer
            quote = item["quote"]
            if not isinstance(quote, str) or not quote.strip() or quote not in text:
                raise ValueError("evidence_quote_not_exact")
            clean.append({"source": source, "quote": quote})
        return clean

    def _V10Review__strings(value, *, nonempty=False):
        if not isinstance(value, list) or not all(isinstance(x, str) and x.strip() for x in value):
            raise ValueError("nonempty_string_array_required")
        result = list(dict.fromkeys(value))
        if nonempty and not result:
            raise ValueError("nonempty_string_array_required")
        return result

    def _V10Review__facet_names(value, *, required):
        names = _V10Review__strings(value)
        if (required and not names) or any(name not in _V10Review_FACETS for name in names):
            raise ValueError("issue_facets_invalid")
        return [name for name in _V10Review_FACETS if name in names]

    def _V10Review_route_issues(
        value, problem, answer, *, admitted_ids=(), rejected_ids=(), seen_issue_ids=()
    ):
        # fmt: off
        """Return separate candidate triggers, active check objections, diagnostics.

    `seen_issue_ids` belongs to the current candidate in the caller.  Only check
    objections with currently admitted IDs survive; rejected or unknown IDs are
    diagnostic data and never become repair triggers.  Fields are projected, so
    untrusted arbitrary payloads do not propagate to the next request.
    """
        # fmt: on
        result = {"candidate_issues": [], "check_objections": [], "ignored": []}
        if not isinstance(value, list):
            result["ignored"].append({"id": "", "reason": "issues_array_required"})
            return result
        active, rejected, seen = set(admitted_ids), set(rejected_ids), set(seen_issue_ids)
        for item in value:
            ident = item.get("id", "") if isinstance(item, dict) else ""
            try:
                if not isinstance(ident, str) or not ident.strip():
                    raise ValueError("issue_id_required")
                if ident in seen:
                    raise ValueError("issue_duplicate_or_already_seen")
                subject = item.get("subject")
                if subject not in {"candidate", "check"}:
                    raise ValueError("issue_subject_required")
                if item.get("basis") != _V10Review_VISIBLE_BASIS:
                    raise ValueError("issue_not_based_on_visible_requirement")
                defect = item.get("defect")
                if not isinstance(defect, str) or not defect.strip():
                    raise ValueError("issue_defect_required")
                evidence = _V10Review__evidence(item.get("evidence"), problem, answer)
                check_ids = _V10Review__strings(item.get("check_ids"))
                facets = _V10Review__facet_names(
                    item.get("facets", []), required=subject == "check"
                )
                if subject == "check":
                    inactive = [x for x in check_ids if x not in active or x in rejected]
                    check_ids = [x for x in check_ids if x in active and x not in rejected]
                    if not check_ids:
                        raise ValueError("check_issue_has_no_currently_admitted_ids")
                    if inactive:
                        result["ignored"].append(
                            {
                                "id": ident,
                                "reason": "inactive_check_ids_removed",
                                "check_ids": inactive,
                            }
                        )
                clean = {
                    "id": ident,
                    "subject": subject,
                    "defect": defect,
                    "basis": _V10Review_VISIBLE_BASIS,
                    "evidence": evidence,
                    "check_ids": check_ids,
                    "facets": facets,
                }
            except (KeyError, TypeError, ValueError) as error:
                result["ignored"].append(
                    {"id": ident if isinstance(ident, str) else "", "reason": str(error)}
                )
                continue
            seen.add(ident)
            result["candidate_issues" if subject == "candidate" else "check_objections"].append(
                clean
            )
        return result

    def _V10Review__objections(diagnosis, ids, problem, answer):
        """Project labels/evidence/facets; never copy free model reasoning."""
        raw = diagnosis.get("check_objections", []) if isinstance(diagnosis, dict) else []
        if not isinstance(raw, list):
            return []
        result = []
        for item in raw:
            try:
                if not isinstance(item, dict) or item.get("basis") != _V10Review_VISIBLE_BASIS:
                    continue
                check_ids = [
                    x for x in _V10Review__strings(item.get("check_ids"), nonempty=True) if x in ids
                ]
                if not check_ids:
                    continue
                facets = _V10Review__facet_names(item.get("facets"), required=True)
                kind = item.get("objection_kind")
                canonical = {
                    "check_ids": check_ids,
                    "basis": _V10Review_VISIBLE_BASIS,
                    "evidence": _V10Review__evidence(item.get("evidence"), problem, answer),
                    "facets": facets,
                }
                if isinstance(kind, str) and kind in _V10Review_OBJECTION_REASONS:
                    canonical.update(objection_kind=kind, reason=_V10Review_OBJECTION_REASONS[kind])
                else:
                    canonical["reason"] = (
                        "Reassess these check facets against the quoted visible evidence: "
                        + ", ".join(facets)
                        + "."
                    )
                result.append(canonical)
            except (KeyError, TypeError, ValueError):
                continue
        return result

    def _V10Review__typed_projection(value):
        """Copy typed check data, never arbitrary nested diagnostic fields."""
        if not isinstance(value, dict):
            raise ValueError("typed_check_value_required")
        tag = value.get("type")
        if tag == "none":
            return {"type": tag}
        scalar_types = {"bool": bool, "int": int, "float": float, "str": str}
        if tag in scalar_types and type(value.get("value")) is scalar_types[tag]:
            return {"type": tag, "value": value["value"]}
        if tag in {"list", "tuple"} and isinstance(value.get("items"), list):
            return {"type": tag, "items": [_V10Review__typed_projection(x) for x in value["items"]]}
        if tag == "dict" and isinstance(value.get("items"), list):
            return {
                "type": tag,
                "items": [
                    {
                        "key": _V10Review__typed_projection(x["key"]),
                        "value": _V10Review__typed_projection(x["value"]),
                    }
                    for x in value["items"]
                ],
            }
        raise ValueError("typed_check_value_invalid")

    def _V10Review__check_projection(check, problem, answer):
        if not isinstance(check, dict) or not isinstance(check.get("id"), str):
            raise ValueError("check_id_required")
        clean = {
            "id": check["id"],
            "kind": check["kind"],
            "args": [_V10Review__typed_projection(x) for x in check["args"]],
            "kwargs": {
                key: _V10Review__typed_projection(value) for key, value in check["kwargs"].items()
            },
            "evidence": _V10Review__evidence(check["evidence"], problem, answer),
            "derivation": _V10Review_BLIND_DERIVATION,
        }
        if not isinstance(check.get("derivation"), str):
            raise ValueError("check_derivation_required")
        if check["kind"] == "exact":
            if check["target"] not in {"return", "stdout"}:
                raise ValueError("check_target_invalid")
            clean.update(
                target=check["target"], expected=_V10Review__typed_projection(check["expected"])
            )
        elif check["kind"] == "property":
            prop = check["property"]
            name = prop["name"]
            clean["property"] = {"name": name}
            if name == "return_type":
                clean["property"]["type"] = prop["type"]
            elif name in {"length_equals_input", "same_type_as_input"}:
                clean["property"]["input"] = {
                    key: _V10Review_copy.deepcopy(value)
                    for key, value in prop["input"].items()
                    if key in {"arg", "kwarg"}
                }
            elif name == "numeric_value":
                clean["property"]["expected"] = _V10Review__typed_projection(prop["expected"])
            elif name == "truthiness":
                if type(prop.get("expected")) is not bool:
                    raise ValueError("truthiness_expectation_must_be_bool")
                clean["property"]["expected"] = prop["expected"]
            elif name == "stdout_content":
                expected = _V10Review__typed_projection(prop["expected"])
                if expected["type"] != "str":
                    raise ValueError("stdout_content_expectation_must_be_typed_string")
                clean["property"]["expected"] = expected
            elif name != "nonmutation":
                raise ValueError("check_property_invalid")
        else:
            raise ValueError("check_kind_invalid")
        return clean

    def _V10Review_blind_challenge_payload(
        context, checks, diagnosis, *, problem=None, answer=None
    ):
        # fmt: off
        """Allowlist visible inputs plus check-only objections for blind admission.

    Candidate/code/observations/brief/trigger/diagnosis fields are not copied.
    Objection reasons are fixed locally from allowlisted labels or facet names;
    no free model prose is forwarded. The objections remain fallible, and the
    independent admission must establish all six facets itself.
    Only checks with a valid structured objection are included.
    """
        # fmt: on
        problem = context.get("task") if problem is None else problem
        answer = context.get("actual_answer", "") if answer is None else answer
        if (
            not isinstance(problem, dict)
            or not isinstance(problem.get("prompt"), str)
            or not isinstance(problem.get("entry_point"), str)
            or not isinstance(answer, str)
        ):
            raise ValueError("visible_context_required")
        projected = []
        for check in checks:
            try:
                projected.append(_V10Review__check_projection(check, problem, answer))
            except (AttributeError, KeyError, TypeError, ValueError):
                continue
        objections = _V10Review__objections(
            diagnosis, {check["id"] for check in projected}, problem, answer
        )
        challenged = {ident for item in objections for ident in item["check_ids"]}
        payload = {
            "task": {"prompt": problem["prompt"], "entry_point": problem["entry_point"]},
            "actual_question": context.get("actual_question", "")
            if isinstance(context.get("actual_question", ""), str)
            else "",
            "actual_answer": answer,
            "proposed_checks": [check for check in projected if check["id"] in challenged],
            "check_objections": objections,
        }
        for field, expected in (("qa_epoch", int), ("qa_hash", str)):
            if type(context.get(field)) is expected:
                payload[field] = context[field]
        return payload

    def _V10Review_validate_facet_admission(value, proposals, problem, answer):
        # fmt: off
        """Return (accepted IDs, rejected diagnostics), failing closed per check.

    The value facet is mandatory for property checks as well as exact checks.
    Bare reviewer accepted IDs, `relevant: false`, truthy strings, omitted facets,
    and unquoted model confidence cannot bypass independent admission.
    """
        # fmt: on
        assessments = value.get("check_assessments") if isinstance(value, dict) else None
        records, duplicate = {}, set()
        for item in assessments if isinstance(assessments, list) else []:
            if isinstance(item, dict) and isinstance(item.get("id"), str):
                ident = item["id"]
                if ident in records:
                    duplicate.add(ident)
                records[ident] = item
        accepted, rejected = [], []
        for proposal in proposals:
            ident = proposal["id"]
            try:
                if ident in duplicate:
                    raise ValueError("facet_assessment_duplicate")
                item = records.get(ident)
                if item is None:
                    raise ValueError("facet_assessment_missing")
                facets = item.get("facets")
                if not isinstance(facets, dict) or set(facets) != set(_V10Review_FACETS):
                    raise ValueError("all_six_facets_required")
                for name in _V10Review_FACETS:
                    facet = facets[name]
                    if not isinstance(facet, dict) or facet.get("known") is not True:
                        raise ValueError(name + "_not_known_true")
                    if facet.get("verdict", "supported") != "supported":
                        raise ValueError(name + "_positive_verdict_invalid")
                    if facet.get("relevant", True) is not True:
                        raise ValueError(name + "_irrelevance_is_not_admission")
                    if not isinstance(facet.get("reason"), str) or not facet["reason"].strip():
                        raise ValueError(name + "_reason_required")
                    _V10Review__evidence(facet.get("evidence"), problem, answer)
            except (KeyError, TypeError, ValueError) as error:
                rejected.append({"id": ident, "reason": str(error)})
                continue
            accepted.append(ident)
        return accepted, rejected

    def _V10Review_facet_admission_ids(value, proposals, problem, answer):
        return _V10Review_validate_facet_admission(value, proposals, problem, answer)[0]

    def _V10Review_conclusive_rejection_ids(value, proposals, problem, answer):
        # fmt: off
        """Identify explicit grounded contradictions in a candidate-blind challenge.

    Initial admission and revocation are different gates.  A missing, malformed,
    unknown, duplicate or stale assessment is insufficient to revoke an existing
    check.  One grounded negative facet can refute a check even if other complete
    facet objects explicitly report unknown.  No candidate information is used.
    """
        # fmt: on
        assessments = value.get("check_assessments") if isinstance(value, dict) else None
        if not isinstance(assessments, list):
            return []
        records, duplicates = {}, set()
        for item in assessments:
            if isinstance(item, dict) and isinstance(item.get("id"), str):
                ident = item["id"]
                if ident in records:
                    duplicates.add(ident)
                records[ident] = item
        rejected = []
        for proposal in proposals:
            ident = proposal["id"]
            if ident not in records or ident in duplicates:
                continue
            try:
                facets = records[ident].get("facets")
                if not isinstance(facets, dict) or set(facets) != set(_V10Review_FACETS):
                    continue
                contradicted = False
                for name in _V10Review_FACETS:
                    facet = facets[name]
                    if not isinstance(facet, dict) or type(facet.get("known")) is not bool:
                        raise ValueError("facet_state_malformed")
                    if not isinstance(facet.get("reason"), str) or not facet["reason"].strip():
                        raise ValueError("facet_reason_missing")
                    if not isinstance(facet.get("evidence"), list):
                        raise ValueError("facet_evidence_array_required")
                    if facet.get("relevant", True) is not True:
                        raise ValueError("irrelevance_is_not_a_contradiction")
                    known, verdict = (
                        facet["known"],
                        facet.get("verdict", "supported" if facet["known"] else None),
                    )
                    if known:
                        if verdict != "supported" or facet.get("relevant", True) is not True:
                            raise ValueError("positive_facet_malformed")
                        _V10Review__evidence(facet["evidence"], problem, answer)
                    elif verdict == "contradicted":
                        _V10Review__evidence(facet["evidence"], problem, answer)
                        contradicted = True
                    elif verdict == "unknown":
                        if facet["evidence"]:
                            _V10Review__evidence(facet["evidence"], problem, answer)
                    else:
                        raise ValueError("negative_facet_verdict_required")
                if contradicted:
                    rejected.append(ident)
            except (KeyError, TypeError, ValueError):
                continue
        return rejected

    # Frozen source: pilot/intentbridge_v3_20261101/algorithm.py
    """TRAIN-informed independent revision; model effectiveness is not yet measured.

Only visible task/Q/A and supplied environment methods are used. The complete
frozen v2 remains a dependency, never patched. All model-produced requirements
and probes remain fallible. One run returns one program without hidden scoring.
"""

    import copy as _V10V3_copy
    import json as _V10V3_json
    import keyword as _V10V3_keyword

    _V10V3_DEFAULT_POLICY = {
        "plan_guidance": (
            "Compare unresolved choices by their consequence for the main computation on legal inputs. "
            "Ask an open neutral question when proposed alternatives do not exhaust the possibilities. "
            "Include the complete input in a distinguishing question. A missing signature is unknown, "
            "and a narrow answer does not settle unrelated choices. No category has automatic priority."
        ),
        "solve_guidance": (
            "Treat the full visible task and literal answer as authority. A structured brief is a fallible aid; "
            "retain confirmed facts if another citation fails. A probe is not a new requirement. "
            "Do not extend a callable or reinterpret input data to satisfy a check without visible interface evidence. "
            "Keep Python types, literal escapes, printing, and truthiness distinct."
        ),
    }

    _V10V3_REFERENCE_INSTRUCTIONS = """Evidence may be {source:'prompt'|'actual_answer',
span_id:ID} using the supplied evidence_catalog, or {source:SOURCE,quote:EXACT_TEXT}.
Span IDs bind this complete task and actual Q/A. They identify literal source
text, not a proof that a fact follows from it. Do not copy IDs from prior tasks.
"""

    _V10V3_BRIEF_INSTRUCTIONS = (
        _V10V2_GROUNDING
        + _V10V3_REFERENCE_INSTRUCTIONS
        + """Write a SHORT
implementation brief with {confirmed:[{fact:string,evidence:[EVIDENCE]}],
scope_updates:[{fact:string,evidence:[EVIDENCE]}],unresolved:[string]}.
Each scope update must cite actual_answer. Separate missing information from
prohibitions and preserve unrelated task requirements. Use supplied span IDs
to avoid paraphrasing exact evidence. Valid facts survive a different fact's
citation error; they still do not override the literal task or answer.
"""
    )

    _V10V3_CHECK_OBJECT_SCHEMA = """CHECK is {id:string,args:[TYPED],kwargs:{name:TYPED},
evidence:[EVIDENCE],derivation:string} plus either
{kind:'exact',target:'return'|'stdout',expected:TYPED} or
{kind:'property',property:PROPERTY}. PROPERTY is
{name:'return_type',type:TYPE}, {name:'length_equals_input',input:{arg:INDEX}|{kwarg:NAME}},
{name:'same_type_as_input',input:{arg:INDEX}|{kwarg:NAME}}, {name:'nonmutation'},
{name:'numeric_value',expected:TYPED_NUMBER}, {name:'truthiness',expected:BOOL}, or
{name:'stdout_content',expected:TYPED_STRING}. TYPE is none/bool/int/float/str/list/tuple/dict.
"""

    _V10V3_CANDIDATE_REVIEW_INSTRUCTIONS = (
        _V10V2_GROUNDING
        + _V10V3_REFERENCE_INSTRUCTIONS
        + _V10Review_REVIEW_INSTRUCTIONS
        + _V10Checks_CHECK_SEMANTICS_INSTRUCTIONS
        + _V10V2_TYPED_INSTRUCTIONS
        + _V10V3_CHECK_OBJECT_SCHEMA
        + """Inspect the candidate against the complete task and actual Q/A.
Only admitted checks may constrain code. Treat rejected/unknown checks as
fallible diagnostics. Convert a concrete candidate defect into at most TWO
additional grounded checks when possible; each receives separate candidate-blind
admission. Do not invent expected values to justify a preferred repair.
JSON {issues:[ISSUE],additional_checks:[CHECK],unresolved:[string],reason:string}.
"""
    )

    class _V10V3__Run(_V10V2__Run):
        def __init__(self, config, policy, problem, *, conditioned=False):
            super().initialize(config, policy, problem, conditioned=conditioned)
            self.artifacts["variant"] = "intentbridge_v3_train_informed"
            self.artifacts.update(
                brief_validation=[],
                evidence_rejections=[],
                issue_routing=[],
                check_objections=[],
                blind_admissions=[],
            )
            self.artifacts["mechanisms"].update(
                {
                    "brief_partial_retained": 0,
                    "brief_targeted_repairs": 0,
                    "blind_admission_calls": 0,
                    "check_objection_triggers": 0,
                    "inactive_issue_ignored": 0,
                    "check_challenge_dropped": 0,
                    "candidate_issue_without_distinguishing_check": 0,
                }
            )

        def catalog(self):
            return _V10Evidence_build_evidence_catalog(
                self.problem, self.qa[1], question=self.qa[0]
            )

        def context(self):
            return {**super().context(), "evidence_catalog": self.catalog()}

        def canonical(self, value, *, phase, path="$"):
            """Resolve evidence locally; malformed evidence stays invalid, not guessed."""
            if isinstance(value, list):
                return [
                    self.canonical(item, phase=phase, path=f"{path}[{i}]")
                    for i, item in enumerate(value)
                ]
            if not isinstance(value, dict):
                return _V10V3_copy.deepcopy(value)
            result = {}
            for key, item in value.items():
                if key in {"args", "kwargs", "expected", "property"}:
                    # Executable check data can legitimately contain an argument
                    # named "evidence". It is data, never a citation surface.
                    result[key] = _V10V3_copy.deepcopy(item)
                elif key == "evidence":
                    try:
                        result[key] = _V10Evidence_resolve_evidence(
                            item,
                            self.problem,
                            self.qa[1],
                            catalog=self.catalog(),
                            question=self.qa[0],
                            path=path + ".evidence",
                        )
                    except EvidenceValidationError as error:
                        result[key] = []
                        self.artifacts["evidence_rejections"].append(
                            {"phase": phase, "errors": error.errors}
                        )
                else:
                    result[key] = self.canonical(item, phase=phase, path=path + "." + str(key))
            return result

        def brief(self, env):
            messages = [
                {
                    "role": "user",
                    "content": _V10V3_BRIEF_INSTRUCTIONS
                    + _V10V3_json.dumps(self.context(), ensure_ascii=False),
                }
            ]
            checked = None
            paths = []
            for attempt in range(self.config["repair_attempts"] + 1):
                raw = env.llm(messages)
                try:
                    value = _V10Original_json_object(raw)
                except (AttributeError, KeyError, TypeError, ValueError, RecursionError):
                    value = None
                if checked is None:
                    checked = _V10Evidence_validate_brief_partial(
                        value, self.problem, self.qa[1], catalog=self.catalog(), question=self.qa[0]
                    )
                else:
                    checked = _V10Evidence_merge_brief_repair(
                        checked,
                        value,
                        self.problem,
                        self.qa[1],
                        repair_paths=paths,
                        catalog=self.catalog(),
                        question=self.qa[0],
                    )
                self.artifacts["brief_validation"].append(
                    {
                        "attempt": attempt,
                        "errors": _V10V3_copy.deepcopy(checked["errors"]),
                        "valid_paths": checked["valid_paths"],
                        "context_sha256": checked["context_sha256"],
                    }
                )
                if not checked["errors"]:
                    break
                self.record(
                    phase="implementation_brief",
                    status="partial_validation",
                    attempt=attempt,
                    detail=_V10V3_json.dumps(checked["errors"], ensure_ascii=False),
                )
                if attempt < self.config["repair_attempts"]:
                    self.count("brief_targeted_repairs")
                    self.count("format_repairs")
                    paths = list(dict.fromkeys(error["path"] for error in checked["errors"]))
                    messages.extend(
                        [
                            {"role": "assistant", "content": raw if isinstance(raw, str) else ""},
                            {
                                "role": "user",
                                "content": "Repair only the indicated paths using current visible evidence. "
                                "Keep original list indices; return the same three-field brief object. Do not alter valid "
                                "untargeted facts. For any scope_updates repair return its entire current replacement list. "
                                "Use exact span IDs; unsupported facts may be removed, never invented.\n"
                                + _V10V3_json.dumps(
                                    {
                                        "errors": checked["errors"],
                                        "valid_paths": checked["valid_paths"],
                                        "retained_verified_brief": checked["brief"],
                                        "evidence_catalog": self.catalog(),
                                    },
                                    ensure_ascii=False,
                                ),
                            },
                        ]
                    )
            value = checked["brief"]
            has_facts = bool(value["confirmed"] or value["scope_updates"])
            if checked["errors"] and has_facts:
                self.count("brief_partial_retained")
            if has_facts:
                self.count("brief_valid")
            else:
                self.count("brief_fallback")
                value["unresolved"].append(
                    "Use the complete original task and literal Q/A; no structured fact was accepted."
                )
            value.update(
                fallback=not has_facts,
                partial=bool(checked["errors"]),
                qa_epoch=self.epoch,
                qa_hash=self.digest,
            )
            self.artifacts["implementation_brief"] = value

        def checks_from(self, value, *, limit, existing_ids=()):
            value = self.canonical(value, phase="check_schema")
            try:
                proposals, rejected = _V10Checks_validate_checks(
                    value, self.problem, self.qa[1], existing_ids=existing_ids, limit=limit
                )
            except (TypeError, ValueError):
                proposals, rejected = [], [{"id": "", "reason": "checks_schema_unavailable"}]
            self.artifacts["checks"]["proposed"].extend(_V10V3_copy.deepcopy(proposals))
            self.artifacts["checks"]["rejected"].extend(rejected)
            self.count("check_proposed", len(proposals) + len(rejected))
            self.count("check_rejected", len(rejected))
            return proposals

        def blind_assess(self, env, proposals, *, diagnosis=None):
            if not proposals:
                return {"accepted_ids": [], "rejected": [], "conclusive_rejected_ids": []}
            if diagnosis is None:
                payload = {
                    "task": self.problem,
                    "actual_question": self.qa[0],
                    "actual_answer": self.qa[1],
                    "qa_hash": self.digest,
                    "qa_epoch": self.epoch,
                    "proposed_checks": [
                        {**_V10V3_copy.deepcopy(p), "derivation": _V10Review_BLIND_DERIVATION}
                        for p in proposals
                    ],
                }
            else:
                payload = _V10Review_blind_challenge_payload(
                    self.context(), proposals, diagnosis, problem=self.problem, answer=self.qa[1]
                )
                if not payload["proposed_checks"]:
                    return {
                        "accepted_ids": [],
                        "rejected": [
                            {"id": p["id"], "reason": "no_valid_current_check_objection"}
                            for p in proposals
                        ],
                        "conclusive_rejected_ids": [],
                    }
                proposals = payload["proposed_checks"]
            payload["evidence_catalog"] = self.catalog()
            self.count("blind_admission_calls")
            result = self.json_call(
                env,
                _V10V2_GROUNDING
                + _V10V3_REFERENCE_INSTRUCTIONS
                + _V10Review_FACET_INSTRUCTIONS
                + _V10Checks_CHECK_SEMANTICS_INSTRUCTIONS,
                payload,
                "blind_check_admission",
            )
            result = self.canonical(result, phase="blind_check_admission")
            accepted, rejected = _V10Review_validate_facet_admission(
                result, proposals, self.problem, self.qa[1]
            )
            conclusive = _V10Review_conclusive_rejection_ids(
                result, proposals, self.problem, self.qa[1]
            )
            self.artifacts["blind_admissions"].append(
                {
                    "qa_hash": self.digest,
                    "check_ids": [p["id"] for p in proposals],
                    "accepted_ids": accepted,
                    "rejected": rejected,
                    "challenge": diagnosis is not None,
                    "conclusive_rejected_ids": conclusive,
                    "candidate_code_or_observations_supplied": False,
                }
            )
            self.artifacts["checks"]["reviews"].append(_V10V3_copy.deepcopy(result))
            return {
                "accepted_ids": accepted,
                "rejected": rejected,
                "conclusive_rejected_ids": conclusive,
            }

        def admit(self, proposals, accepted_ids):
            good = [p for p in proposals if p["id"] in accepted_ids]
            bad = [
                {"id": p["id"], "reason": "independent_facets_not_admitted"}
                for p in proposals
                if p["id"] not in accepted_ids
            ]
            existing = {p["id"] for p in self.artifacts["checks"]["admitted"]}
            good = [p for p in good if p["id"] not in existing]
            self.artifacts["checks"]["admitted"].extend(_V10V3_copy.deepcopy(good))
            self.artifacts["checks"]["rejected"].extend(bad)
            self.count("check_admitted", len(good))
            self.count("check_rejected", len(bad))

        def review(self, env, candidate, proposals, *, additions=False):
            if additions and proposals:
                assessment = self.blind_assess(env, proposals)
                self.admit(proposals, assessment["accepted_ids"])
            value = (
                self.json_call(
                    env,
                    _V10V3_CANDIDATE_REVIEW_INSTRUCTIONS
                    + ("\nReturn additional_checks: [] in this review.\n" if not additions else ""),
                    {
                        **self.context(),
                        "candidate": candidate["code"],
                        "admitted_checks": self.artifacts["checks"]["admitted"],
                        "rejected_check_ids": [
                            p["id"] for p in self.artifacts["checks"]["rejected"]
                        ],
                    },
                    "candidate_review",
                )
                or {}
            )
            value = self.canonical(value, phase="candidate_review")
            if additions:
                existing = {p["id"] for p in self.artifacts["checks"]["proposed"]} | {
                    p["id"] for p in self.artifacts["checks"]["admitted"]
                }
                remaining = max(0, _V10V2_MAX_CHECKS - len(self.artifacts["checks"]["admitted"]))
                extra = self.checks_from(
                    {"checks": value.get("additional_checks", [])},
                    limit=min(2, remaining),
                    existing_ids=existing,
                )
                if extra:
                    assessment = self.blind_assess(env, extra)
                    self.admit(extra, assessment["accepted_ids"])
            active = {p["id"] for p in self.artifacts["checks"]["admitted"]}
            routed = _V10Review_route_issues(
                value.get("issues", []),
                self.problem,
                self.qa[1],
                admitted_ids=active,
                rejected_ids=[
                    p["id"] for p in self.artifacts["checks"]["rejected"] if p["id"] not in active
                ],
            )
            self.count("inactive_issue_ignored", len(routed["ignored"]))
            self.artifacts["issue_routing"].append(_V10V3_copy.deepcopy(routed))
            clean = {
                "candidate_id": candidate["candidate_id"],
                "qa_hash": self.digest,
                "issues": routed["candidate_issues"],
                "check_objections": routed["check_objections"],
                "unresolved": value.get("unresolved", []),
                "reason": value.get("reason", ""),
            }
            self.artifacts["reviews"].append(_V10V3_copy.deepcopy(clean))
            return clean

        def execute_checks(self, env, candidate):
            admitted = self.artifacts["checks"]["admitted"]
            if not admitted:
                candidate["observations"] = []
                return []
            raw = env.exec_code(
                _V10Checks_probe_script(candidate["code"], self.problem["entry_point"], admitted)
            )
            rows = _V10V2_parse_observations(raw, admitted)
            self.artifacts["probe_runs"].append(
                {
                    "candidate_id": candidate["candidate_id"],
                    "qa_hash": self.digest,
                    "raw": raw,
                    "observations": _V10V3_copy.deepcopy(rows),
                }
            )
            self.count("probe_runs")
            candidate["observations"] = rows
            return rows

        def choose_visible_best(self):
            self.best = None
            admitted = self.artifacts["checks"]["admitted"]
            for candidate in self.artifacts["candidates"]:
                if (
                    candidate["eligible"]
                    and candidate["qa_hash"] == self.digest
                    and candidate["observations"] is not None
                ):
                    if self.best is None or self.passed(self.best, admitted) < self.passed(
                        candidate, admitted
                    ):
                        self.best = candidate

        def challenge(self, env, ids, diagnosis=None):
            contested = [p for p in self.artifacts["checks"]["admitted"] if p["id"] in ids]
            if not contested or diagnosis is None:
                return False
            self.count("check_challenged", len(contested))
            payload = _V10Review_blind_challenge_payload(
                self.context(), contested, diagnosis, problem=self.problem, answer=self.qa[1]
            )
            targeted = {p["id"] for p in payload["proposed_checks"]}
            if not targeted:
                return False
            assessment = self.blind_assess(env, contested, diagnosis=diagnosis)
            dropped = targeted.intersection(assessment["conclusive_rejected_ids"])
            self.artifacts["check_objections"].append(
                {
                    "qa_hash": self.digest,
                    "payload": payload,
                    "dropped_ids": sorted(dropped),
                    "rejections": assessment["rejected"],
                }
            )
            if dropped:
                self.artifacts["checks"]["admitted"] = [
                    p for p in self.artifacts["checks"]["admitted"] if p["id"] not in dropped
                ]
                self.artifacts["checks"]["rejected"].extend(
                    {"id": ident, "reason": "blind_facet_contradicted_on_challenge"}
                    for ident in sorted(dropped)
                )
                self.count("check_rejected", len(dropped))
                self.count("check_challenge_dropped", len(dropped))
                self.choose_visible_best()
            return bool(dropped)

        def diagnosis(self, env, trigger, reviewed):
            def schema(value):
                if (
                    value.get("action") not in {"repair", "challenge_checks", "stop"}
                    or not isinstance(value.get("diagnosis"), str)
                    or not isinstance(value.get("target"), str)
                ):
                    raise ValueError("diagnosis_schema_invalid")
                if value["action"] != "stop":
                    value["evidence"] = _V10Evidence_resolve_evidence(
                        value.get("evidence"),
                        self.problem,
                        self.qa[1],
                        catalog=self.catalog(),
                        question=self.qa[0],
                    )
                if value["action"] == "challenge_checks":
                    value = self.canonical(value, phase="diagnosis")
                    active = self.artifacts["checks"]["admitted"]
                    payload = _V10Review_blind_challenge_payload(
                        self.context(), active, value, problem=self.problem, answer=self.qa[1]
                    )
                    if not payload["check_objections"]:
                        raise ValueError("structured_current_check_objection_required")
                    value["challenged_check_ids"] = list(
                        dict.fromkeys(p["id"] for p in payload["proposed_checks"])
                    )
                else:
                    value["challenged_check_ids"] = []
                return value

            result = self.json_call(
                env,
                _V10V2_DIAGNOSE_INSTRUCTIONS
                + _V10V3_REFERENCE_INSTRUCTIONS
                + _V10Review_DIAGNOSIS_INSTRUCTIONS
                + _V10Checks_CHECK_SEMANTICS_INSTRUCTIONS,
                {
                    **self.context(),
                    "trigger": trigger,
                    "candidate": self.best,
                    "admitted_checks_fallible": self.artifacts["checks"]["admitted"],
                    "review": reviewed,
                },
                "failure_diagnosis",
                schema,
            )
            if result is not None:
                self.artifacts["diagnoses"].append(
                    {
                        "candidate_id": self.best["candidate_id"] if self.best else None,
                        "qa_hash": self.digest,
                        **_V10V3_copy.deepcopy(result),
                    }
                )
            return result

        def implement(self, env):
            self.brief(env)
            candidate = self.generate(env, {"kind": "initial_synthesis"})
            if (
                candidate is None
                and len(self.artifacts["candidates"]) < self.config["max_candidates"]
            ):
                self.count("repair_triggers")
                self.count("structural_recovery_triggers")
                candidate = self.generate(
                    env,
                    {
                        "kind": "structural_failure",
                        "previous_errors": self.artifacts["candidates"][-1]["format_errors"],
                    },
                )
                if candidate is not None:
                    self.count("repair_accepted")
                    candidate["selection_reason"] = "first_valid_current_qa_structural_recovery"
            if candidate is None:
                self.artifacts["status"] = "no_current_qa_valid_implementation"
                return
            self.best = candidate
            value = self.json_call(
                env,
                _V10V2_CHECK_INSTRUCTIONS
                + _V10V3_REFERENCE_INSTRUCTIONS
                + _V10Checks_CHECK_SEMANTICS_INSTRUCTIONS,
                self.context(),
                "visible_check_generation",
            )
            proposals = self.checks_from(value, limit=4)
            reviewed = self.review(env, candidate, proposals, additions=True)
            if self.execute_checks(env, candidate) is None:
                self.artifacts["status"] = "sandbox_observation_unknown_preserve_candidate"
                return
            seen_codes, seen_issues = {candidate["code"]}, set()
            for round_id in range(self.config["semantic_rounds"] + 1):
                current_code = self.best["code"]
                objections = [
                    item
                    for item in reviewed["check_objections"]
                    if (current_code, "check", item["id"]) not in seen_issues
                ]
                if objections:
                    self.count("check_objection_triggers", len(objections))
                    seen_issues.update((current_code, "check", item["id"]) for item in objections)
                    diagnosis = {
                        "check_objections": [
                            {
                                "check_ids": item["check_ids"],
                                "reason": item["defect"],
                                "basis": item["basis"],
                                "evidence": item["evidence"],
                                "facets": item["facets"],
                            }
                            for item in objections
                        ]
                    }
                    self.challenge(
                        env,
                        [ident for item in objections for ident in item["check_ids"]],
                        diagnosis,
                    )
                    if self.best["code"] != current_code:
                        # A review of the replaced candidate is not a review of the
                        # newly retained one after checks were revoked.
                        reviewed = {**reviewed, "issues": [], "check_objections": []}
                        current_code = self.best["code"]
                admitted = self.artifacts["checks"]["admitted"]
                passed = self.passed(self.best, admitted)
                failures = [
                    r
                    for r in self.best["observations"]
                    if r["id"] in {p["id"] for p in admitted} and r["status"] != "pass"
                ]
                issues = [
                    item
                    for item in reviewed["issues"]
                    if (current_code, "candidate", item["id"]) not in seen_issues
                ]
                self.artifacts["rounds"].append(
                    {
                        "round": round_id,
                        "candidate_id": self.best["candidate_id"],
                        "qa_hash": self.digest,
                        "admitted_check_ids": [p["id"] for p in admitted],
                        "passed_check_ids": sorted(passed),
                        "failures": _V10V3_copy.deepcopy(failures),
                        "issues": issues,
                    }
                )
                if not failures:
                    if issues:
                        self.count("candidate_issue_without_distinguishing_check", len(issues))
                        self.artifacts["status"] = (
                            "review_defect_without_distinguishing_check_preserve_candidate"
                        )
                    else:
                        self.artifacts["status"] = (
                            "visible_checks_satisfied"
                            if admitted
                            else "no_grounded_checks_preserve_candidate"
                        )
                    return
                if (
                    round_id == self.config["semantic_rounds"]
                    or len(self.artifacts["candidates"]) >= self.config["max_candidates"]
                ):
                    self.artifacts["status"] = "bounded_stop_preserve_visible_best"
                    return
                self.count("repair_triggers")
                self.count("check_failure_triggers")
                diagnosed = self.diagnosis(
                    env,
                    {
                        "kind": "credible_check_failure",
                        "failures": failures,
                        "candidate_issues": issues,
                    },
                    reviewed,
                )
                if diagnosed is None or diagnosed["action"] == "stop":
                    self.artifacts["status"] = "diagnosis_stop_preserve_candidate"
                    return
                if diagnosed["action"] == "challenge_checks":
                    if not self.challenge(env, diagnosed["challenged_check_ids"], diagnosed):
                        self.artifacts["status"] = "challenge_unconfirmed_preserve_candidate"
                        return
                    reviewed = {**reviewed, "issues": [], "check_objections": []}
                    continue
                seen_issues.update((current_code, "candidate", item["id"]) for item in issues)
                revised = self.generate(
                    env, {"kind": "credible_check_failure", "failures": failures}, diagnosed
                )
                if revised is None:
                    self.count("repair_rejected")
                    continue
                if revised["code"] in seen_codes:
                    revised["rejection_reason"] = "duplicate_code_no_progress"
                    self.count("repair_rejected")
                    self.artifacts["status"] = "no_progress_preserve_candidate"
                    return
                seen_codes.add(revised["code"])
                if self.execute_checks(env, revised) is None:
                    revised["rejection_reason"] = "sandbox_observation_unknown"
                    self.count("repair_rejected")
                    self.artifacts["status"] = "repair_observation_unknown_preserve_candidate"
                    return
                if passed < self.passed(revised, admitted):
                    self.best = revised
                    self.count("repair_accepted")
                    revised["selection_reason"] = "strict_check_improvement_without_regression"
                    reviewed = self.review(env, revised, admitted)
                else:
                    revised["rejection_reason"] = (
                        "no_strict_improvement_or_previously_passed_check_regressed"
                    )
                    self.count("repair_rejected")
            self.artifacts["status"] = "bounded_stop_preserve_visible_best"

        initialize = __init__

    class _V10V3_IntentBridgeV3Clarifier(_V10V2_IntentBridgeV2Clarifier):
        """Independent TRAIN-informed code revision, with no measured model result."""

        DEFAULT_CONFIG = dict(_V10V2_IntentBridgeV2Clarifier.DEFAULT_CONFIG)

        def __init__(self, config=None, *, policy=None):
            super().initialize(
                config=config, policy=_V10V3_DEFAULT_POLICY if policy is None else policy
            )

        def localRun(self, env, problem, fixed_qa=None):
            for field, ceiling in self.DEFAULT_CONFIG.items():
                if type(self.config[field]) is not int or not 0 <= self.config[field] <= ceiling:
                    raise ValueError(field + " must be an integer within the fixed default ceiling")
            if self.config["max_candidates"] < 1:
                raise ValueError("max_candidates must allow the initial implementation")
            visible = {"prompt": problem["prompt"], "entry_point": problem["entry_point"]}
            if (
                not isinstance(visible["prompt"], str)
                or not isinstance(visible["entry_point"], str)
                or not visible["entry_point"].isidentifier()
                or _V10V3_keyword.iskeyword(visible["entry_point"])
            ):
                raise ValueError("invalid_visible_task_or_entry_point")
            state = _V10V3__Run(
                dict(self.config),
                _V10V3_copy.deepcopy(self.policy),
                visible,
                conditioned=fixed_qa is not None,
            )
            try:
                return state.execute(env, fixed_qa)
            finally:
                self.artifacts, self.trace = (
                    _V10V3_copy.deepcopy(state.artifacts),
                    _V10V3_copy.deepcopy(state.trace),
                )

        initialize = __init__

    # Frozen source: pilot/intentbridge_v4_20261102/protocol.py
    """Pure protocol guards; no model, evaluator, or candidate execution.

Facet parsing establishes structure only. Literal evidence admission/revocation
must still use the frozen v3 review validators under the complete visible Q/A.
"""

    import copy as _V10Protocol_copy
    import hashlib as _V10Protocol_hashlib
    import json as _V10Protocol_json

    def _V10Protocol_validate_checks(
        value, problem, answer, *, existing_ids=(), limit=_V10V2_MAX_CHECKS
    ):
        # fmt: off
        """Keep v3 proposals unchanged, quarantining nonstring rejected IDs.

    A malformed ID is never repaired or admitted. The caller retains the raw
    provider response separately; diagnostics retain only its Python type.
    """
        # fmt: on
        good, rejected = _V10Checks_validate_checks(
            value, problem, answer, existing_ids=existing_ids, limit=limit
        )
        safe = []
        for rejection in rejected:
            item = _V10Protocol_copy.deepcopy(rejection)
            ident = item.get("id", "")
            if not isinstance(ident, str):
                item["id"] = ""
                item["invalid_id_type"] = _IBTypeName(ident)
            else:
                item["id"] = ident
            safe.append(item)
        return good, safe

    def _V10Protocol__json(value):
        return _V10Protocol_json.dumps(
            value, ensure_ascii=True, sort_keys=True, allow_nan=False, separators=(",", ":")
        )

    def _V10Protocol__proposal_ids(proposals):
        if not isinstance(proposals, list):
            raise ValueError("facet_proposals_array_required")
        ids = []
        for proposal in proposals:
            ident = proposal.get("id") if isinstance(proposal, dict) else None
            if not isinstance(ident, str) or not ident.strip() or ident in ids:
                raise ValueError("facet_proposal_id_invalid_or_duplicate")
            ids.append(ident)
        return ids

    def _V10Protocol__binding(proposals, qa_hash, qa_epoch):
        if (
            not isinstance(qa_hash, str)
            or not qa_hash.strip()
            or type(qa_epoch) is not int
            or qa_epoch < 0
        ):
            raise ValueError("current_qa_binding_required")
        return {
            "qa_hash": qa_hash,
            "qa_epoch": qa_epoch,
            "proposal_sha256": _V10Protocol_hashlib.sha256(
                _V10Protocol__json(proposals).encode("utf-8")
            ).hexdigest(),
        }

    def _V10Protocol__error(ident, code, path):
        return {"id": ident, "code": code, "path": path}

    def _V10Protocol__facet_errors(facet, ident, current):
        errors = []
        if not isinstance(facet, dict):
            return [_V10Protocol__error(ident, "facet_object_required", current)]
        known = facet.get("known")
        if type(known) is not bool:
            errors.append(
                _V10Protocol__error(ident, "facet_known_must_be_bool", current + ".known")
            )
        else:
            # v3 explicitly permits an omitted verdict for known:true. A false
            # state must distinguish uncertainty from a claimed contradiction.
            verdict = facet.get("verdict", "supported" if known else None)
            allowed = ("supported",) if known else ("unknown", "contradicted")
            if verdict not in allowed:
                errors.append(
                    _V10Protocol__error(
                        ident, "facet_verdict_inconsistent_with_known", current + ".verdict"
                    )
                )
        if not isinstance(facet.get("reason"), str) or not facet["reason"].strip():
            errors.append(_V10Protocol__error(ident, "facet_reason_required", current + ".reason"))
        if not isinstance(facet.get("evidence"), list):
            errors.append(
                _V10Protocol__error(ident, "facet_evidence_array_required", current + ".evidence")
            )
        return errors

    def _V10Protocol__assessment_errors(record, ident, path):
        facets = record.get("facets")
        if not isinstance(facets, dict) or set(facets) != set(_V10Review_FACETS):
            return [_V10Protocol__error(ident, "all_six_facets_required", path + ".facets")]
        errors = []
        for name in _V10Review_FACETS:
            errors.extend(_V10Protocol__facet_errors(facets[name], ident, path + ".facets." + name))
        return errors

    def _V10Protocol_parse_facet_response(value, proposals, *, qa_hash, qa_epoch):
        # fmt: off
        """Project unique, structurally complete assessments in proposal order.

    All structurally valid states survive, including unknown/contradicted and
    empty evidence arrays. Citation content and semantic support are deliberately
    left to the existing v3 validators. Extra IDs and every duplicate record are
    rejected. ``invalid_ids`` alone names the permitted targets of a repair.
    """
        # fmt: on
        ids = _V10Protocol__proposal_ids(proposals)
        binding = _V10Protocol__binding(proposals, qa_hash, qa_epoch)
        records, duplicates, errors = {}, set(), []
        if not isinstance(value, dict):
            assessments = []
            errors.append(_V10Protocol__error("", "facet_response_object_required", "$"))
        elif not isinstance(value.get("check_assessments"), list):
            assessments = []
            errors.append(
                _V10Protocol__error("", "check_assessments_array_required", "$.check_assessments")
            )
        else:
            assessments = value["check_assessments"]
        for position, record in enumerate(assessments):
            path = "$.check_assessments[" + str(position) + "]"
            if not isinstance(record, dict):
                errors.append(_V10Protocol__error("", "assessment_object_required", path))
                continue
            ident = record.get("id")
            if not isinstance(ident, str) or not ident.strip():
                errors.append(_V10Protocol__error("", "assessment_id_required", path + ".id"))
                continue
            if ident not in ids:
                errors.append(
                    _V10Protocol__error(ident, "assessment_id_not_proposed", path + ".id")
                )
                continue
            if ident in records:
                duplicates.add(ident)
            records[ident] = (record, path)
        accepted_structure, invalid = [], []
        for ident in ids:
            if ident in duplicates:
                current_errors = [
                    _V10Protocol__error(ident, "facet_assessment_duplicate", "$.check_assessments")
                ]
            elif ident not in records:
                current_errors = [
                    _V10Protocol__error(ident, "facet_assessment_missing", "$.check_assessments")
                ]
            else:
                record, path = records[ident]
                current_errors = _V10Protocol__assessment_errors(record, ident, path)
            if current_errors:
                invalid.append(ident)
                errors.extend(current_errors)
            else:
                accepted_structure.append(_V10Protocol_copy.deepcopy(records[ident][0]))
        reason = value.get("reason", "") if isinstance(value, dict) else ""
        # Unique current records retain already valid facets even when a neighboring
        # facet makes the whole assessment malformed. Ambiguous duplicate records
        # retain no fields: a repair must supply one unambiguous assessment instead.
        retained = [
            _V10Protocol_copy.deepcopy(records[ident][0])
            for ident in ids
            if ident in records and ident not in duplicates
        ]
        return {
            "binding": binding,
            "proposal_ids": ids,
            "invalid_ids": invalid,
            "retained_assessments": retained,
            "errors": errors,
            "response": {
                "check_assessments": accepted_structure,
                "reason": reason if isinstance(reason, str) else "",
            },
        }

    def _V10Protocol__checked_previous(previous, proposals, qa_hash, qa_epoch):
        expected = _V10Protocol__binding(proposals, qa_hash, qa_epoch)
        if not isinstance(previous, dict) or _V10Protocol__json(
            previous.get("binding")
        ) != _V10Protocol__json(expected):
            raise ValueError("facet_repair_context_mismatch")
        old_response = previous.get("response", {})
        reason = old_response.get("reason", "") if isinstance(old_response, dict) else ""
        return _V10Protocol_parse_facet_response(
            {"check_assessments": previous.get("retained_assessments", []), "reason": reason},
            proposals,
            qa_hash=qa_hash,
            qa_epoch=qa_epoch,
        )

    def _V10Protocol__merge_record_fields(original, supplied):
        """Retain valid facets and valid decision fields inside a malformed facet."""
        if original is None:
            return _V10Protocol_copy.deepcopy(supplied)
        result = _V10Protocol_copy.deepcopy(supplied)
        old_facets = original.get("facets")
        if not isinstance(old_facets, dict):
            return result
        if not isinstance(result.get("facets"), dict):
            result["facets"] = {}
        for name in _V10Review_FACETS:
            old = old_facets.get(name)
            if not _V10Protocol__facet_errors(old, original["id"], name):
                result["facets"][name] = _V10Protocol_copy.deepcopy(old)
            elif isinstance(old, dict):
                new = result["facets"].get(name)
                new = _V10Protocol_copy.deepcopy(new) if isinstance(new, dict) else {}
                # A malformed reason/citation must not reopen an otherwise explicit
                # semantic decision, especially an existing unknown/contradiction.
                known = old.get("known")
                verdict = old.get("verdict", "supported" if known is True else None)
                allowed = ("supported",) if known is True else ("unknown", "contradicted")
                if type(known) is bool:
                    # A typed decision is immutable even when its verdict is the
                    # malformed field being repaired. In particular false plus a
                    # missing/invalid verdict must never be repaired into true.
                    new["known"] = known
                    if verdict in allowed:
                        if "verdict" in old:
                            new["verdict"] = old["verdict"]
                        else:
                            new.pop("verdict", None)
                if isinstance(old.get("reason"), str) and old["reason"].strip():
                    new["reason"] = old["reason"]
                if isinstance(old.get("evidence"), list):
                    new["evidence"] = _V10Protocol_copy.deepcopy(old["evidence"])
                for field in set(old) - {"known", "verdict", "reason", "evidence"}:
                    new[field] = _V10Protocol_copy.deepcopy(old[field])
                result["facets"][name] = new
        return result

    def _V10Protocol_merge_facet_repair(previous, repaired_value, proposals, *, qa_hash, qa_epoch):
        # fmt: off
        """Repair only structurally invalid/missing IDs under the same task/Q/A.

    Valid supported, unknown, and contradicted records are never replaced, even
    if a repair response supplies a more positive assessment with the same ID.
    Changed proposal contents or Q/A bindings fail closed. Raw responses remain
    the caller's responsibility. Errors describe the current result and rejected
    repair records; the caller should use ``invalid_ids`` for any retry decision.
    """
        # fmt: on
        prior = _V10Protocol__checked_previous(previous, proposals, qa_hash, qa_epoch)
        # Recompute from the retained records instead of trusting caller-supplied
        # invalid_ids. This also prevents malformed records bypassing the parser.
        targets = [proposal for proposal in proposals if proposal["id"] in prior["invalid_ids"]]
        repair = _V10Protocol_parse_facet_response(
            repaired_value, targets, qa_hash=qa_hash, qa_epoch=qa_epoch
        )
        old_records = {item["id"]: item for item in prior["retained_assessments"]}
        new_records = {item["id"]: item for item in repair["retained_assessments"]}
        merged_records = []
        for proposal in proposals:
            ident = proposal["id"]
            if ident not in prior["invalid_ids"]:
                merged_records.append(_V10Protocol_copy.deepcopy(old_records[ident]))
            elif ident in new_records:
                merged_records.append(
                    _V10Protocol__merge_record_fields(old_records.get(ident), new_records[ident])
                )
            elif ident in old_records:
                merged_records.append(_V10Protocol_copy.deepcopy(old_records[ident]))
        merged = _V10Protocol_parse_facet_response(
            {"check_assessments": merged_records, "reason": prior["response"]["reason"]},
            proposals,
            qa_hash=qa_hash,
            qa_epoch=qa_epoch,
        )
        # Record forbidden extra IDs/duplicates/invalid repaired facets without
        # permitting them to overwrite a previously valid assessment.
        merged["errors"].extend(_V10Protocol_copy.deepcopy(repair["errors"]))
        return merged

    def _V10Protocol_citation_repair_targets(
        parsed, proposals, problem, answer, *, qa_hash, qa_epoch
    ):
        # fmt: off
        """Locate literal citation defects in supported known:true facets only.

    This is a quote/schema check, not entailment assessment. Unsupported semantic
    states and uncertainty are never targets, even if their citations are empty.
    """
        # fmt: on
        checked = _V10Protocol__checked_previous(parsed, proposals, qa_hash, qa_epoch)
        targets = []
        for record in checked["retained_assessments"]:
            facets = record.get("facets")
            if not isinstance(facets, dict):
                continue
            for name in _V10Review_FACETS:
                facet = facets.get(name)
                if (
                    _V10Protocol__facet_errors(facet, record["id"], name)
                    or facet["known"] is not True
                ):
                    continue
                try:
                    _V10Review__evidence(facet["evidence"], problem, answer)
                except (KeyError, TypeError, ValueError) as error:
                    targets.append({"id": record["id"], "facet": name, "errors": [str(error)]})
        return targets

    def _V10Protocol_merge_facet_citation_repairs(
        previous, repaired_value, proposals, problem, answer, *, qa_hash, qa_epoch
    ):
        # fmt: off
        """Apply only exact, valid replacement evidence to current citation targets.

    The response is {citation_repairs:[{id,facet,evidence}]}. Additional model
    decision/reason fields are ignored. Duplicate, non-target, unknown-state, or
    still-invalid citation replacements are rejected without changing state.
    Grounded semantic admission/revocation still belongs to frozen v3 review.
    """
        # fmt: on
        prior = _V10Protocol__checked_previous(previous, proposals, qa_hash, qa_epoch)
        targets = {
            (item["id"], item["facet"])
            for item in _V10Protocol_citation_repair_targets(
                prior, proposals, problem, answer, qa_hash=qa_hash, qa_epoch=qa_epoch
            )
        }
        errors, records, duplicates = [], {}, set()
        rows = repaired_value.get("citation_repairs") if isinstance(repaired_value, dict) else None
        if not isinstance(rows, list):
            rows = []
            errors.append(
                _V10Protocol__error("", "citation_repairs_array_required", "$.citation_repairs")
            )
        for position, item in enumerate(rows):
            path = "$.citation_repairs[" + str(position) + "]"
            ident = item.get("id") if isinstance(item, dict) else None
            facet = item.get("facet") if isinstance(item, dict) else None
            if (
                not isinstance(ident, str)
                or not isinstance(facet, str)
                or (ident, facet) not in targets
            ):
                errors.append(
                    _V10Protocol__error(
                        ident if isinstance(ident, str) else "",
                        "citation_repair_not_targeted",
                        path,
                    )
                )
                continue
            key = (ident, facet)
            if key in records:
                duplicates.add(key)
            records[key] = (item, path)
        retained = _V10Protocol_copy.deepcopy(prior["retained_assessments"])
        by_id = {item["id"]: item for item in retained}
        for key, (item, path) in records.items():
            ident, name = key
            if key in duplicates:
                errors.append(_V10Protocol__error(ident, "citation_repair_duplicate", path))
                continue
            try:
                canonical = _V10Review__evidence(item.get("evidence"), problem, answer)
            except (KeyError, TypeError, ValueError) as error:
                errors.append(
                    _V10Protocol__error(
                        ident, "citation_repair_invalid:" + str(error), path + ".evidence"
                    )
                )
                continue
            by_id[ident]["facets"][name]["evidence"] = canonical
        result = _V10Protocol_parse_facet_response(
            {"check_assessments": retained, "reason": prior["response"]["reason"]},
            proposals,
            qa_hash=qa_hash,
            qa_epoch=qa_epoch,
        )
        result["errors"].extend(errors)
        return result

    # Frozen source: pilot/intentbridge_v4_20261102/algorithm.py
    """Independent development-informed protocol recovery; no new model result.

Frozen v3 remains a dependency and is never patched. Unknown requirements stay
unknown. Only the supplied environment methods and visible task/Q/A are used.
"""

    import copy as _V10V4_copy
    import json as _V10V4_json
    import keyword as _V10V4_keyword

    _V10V4_DEFAULT_POLICY = _V10V4_copy.deepcopy(_V10V3_DEFAULT_POLICY)

    _V10V4_COMPLETION_INSTRUCTIONS = (
        _V10V2_GROUNDING
        + _V10V3_REFERENCE_INSTRUCTIONS
        + _V10Checks_CHECK_SEMANTICS_INSTRUCTIONS
        + _V10V2_TYPED_INSTRUCTIONS
        + _V10V3_CHECK_OBJECT_SCHEMA
        + """The candidate reviewer reported a concrete
visible-requirement issue, but current checks do not distinguish it. Propose at
most TWO checks that follow from the complete visible task and literal answer.
Do not infer an expected result from candidate code, output, or reviewer claims.
Use fresh IDs. If the needed requirement is unresolved, return checks:[] and
state that uncertainty. Each proposal receives independent candidate-blind
admission before execution; an issue alone cannot authorize a code repair.
Return JSON {checks:[CHECK],unresolved:[string],reason:string}.
"""
    )

    class _CompletionObservationUnknown(Exception):
        """Local probe result was unavailable; preserve code, never diagnose a bug."""

    class _V10V4__Run(_V10V3__Run):
        def __init__(self, config, policy, problem, *, conditioned=False):
            super().initialize(config, policy, problem, conditioned=conditioned)
            self.artifacts["variant"] = "intentbridge_v4_protocol_recovery"
            self.artifacts.update(facet_recovery=[], check_completions=[])
            self.candidateReviews, self.completionSeen = {}, set()
            self.artifacts["mechanisms"].update(
                facet_schema_repairs=0,
                facet_citation_repairs=0,
                review_check_completions=0,
                review_check_completion_admitted=0,
            )

        def checks_from(self, value, *, limit, existing_ids=()):
            value = self.canonical(value, phase="check_schema")
            try:
                proposals, rejected = _V10Protocol_validate_checks(
                    value, self.problem, self.qa[1], existing_ids=existing_ids, limit=limit
                )
            except (TypeError, ValueError):
                proposals, rejected = [], [{"id": "", "reason": "checks_schema_unavailable"}]
            self.artifacts["checks"]["proposed"].extend(_V10V4_copy.deepcopy(proposals))
            self.artifacts["checks"]["rejected"].extend(rejected)
            self.count("check_proposed", len(proposals) + len(rejected))
            self.count("check_rejected", len(rejected))
            return proposals

        def blind_assess(self, env, proposals, *, diagnosis=None):
            if not proposals:
                return {"accepted_ids": [], "rejected": [], "conclusive_rejected_ids": []}
            if diagnosis is None:
                payload = {
                    "task": self.problem,
                    "actual_question": self.qa[0],
                    "actual_answer": self.qa[1],
                    "qa_hash": self.digest,
                    "qa_epoch": self.epoch,
                    "proposed_checks": [
                        {**_V10V4_copy.deepcopy(p), "derivation": _V10Review_BLIND_DERIVATION}
                        for p in proposals
                    ],
                }
            else:
                payload = _V10Review_blind_challenge_payload(
                    self.context(), proposals, diagnosis, problem=self.problem, answer=self.qa[1]
                )
                proposals = payload["proposed_checks"]
                if not proposals:
                    return {"accepted_ids": [], "rejected": [], "conclusive_rejected_ids": []}
            payload["evidence_catalog"] = self.catalog()
            instructions = (
                _V10V2_GROUNDING
                + _V10V3_REFERENCE_INSTRUCTIONS
                + _V10Review_FACET_INSTRUCTIONS
                + _V10Checks_CHECK_SEMANTICS_INSTRUCTIONS
            )
            messages = [
                {
                    "role": "user",
                    "content": instructions + _V10V4_json.dumps(payload, ensure_ascii=False),
                }
            ]
            parsed, mode = None, "initial"
            self.count("blind_admission_calls")
            binding = {"qa_hash": self.digest, "qa_epoch": self.epoch}
            for attempt in range(self.config["repair_attempts"] + 1):
                # Provider exceptions escape; only parsing/protocol errors recover.
                raw = env.llm(messages)
                try:
                    value = self.canonical(
                        _V10Original_json_object(raw), phase="blind_check_admission"
                    )
                    if mode == "initial":
                        parsed = _V10Protocol_parse_facet_response(value, proposals, **binding)
                    elif mode == "schema":
                        parsed = _V10Protocol_merge_facet_repair(
                            parsed, value, proposals, **binding
                        )
                    else:
                        parsed = _V10Protocol_merge_facet_citation_repairs(
                            parsed,
                            value,
                            proposals,
                            problem=self.problem,
                            answer=self.qa[1],
                            **binding,
                        )
                except (AttributeError, KeyError, TypeError, ValueError, RecursionError) as error:
                    self.record(
                        phase="blind_check_admission",
                        status="format_error",
                        attempt=attempt,
                        detail=str(error),
                    )
                    if parsed is None:
                        parsed = _V10Protocol_parse_facet_response({}, proposals, **binding)
                invalid = parsed["invalid_ids"]
                targets = _V10Protocol_citation_repair_targets(
                    parsed, proposals, self.problem, self.qa[1], **binding
                )
                self.artifacts["facet_recovery"].append(
                    {
                        "qa_hash": self.digest,
                        "attempt": attempt,
                        "mode": mode,
                        "invalid_ids": list(invalid),
                        "citation_targets": _V10V4_copy.deepcopy(targets),
                        "errors": _V10V4_copy.deepcopy(parsed["errors"]),
                    }
                )
                if not invalid and not targets:
                    break
                if attempt == self.config["repair_attempts"]:
                    self.record(phase="blind_check_admission", status="format_exhausted")
                    break
                mode = "schema" if invalid else "citations"
                self.count("format_repairs")
                self.count("facet_schema_repairs" if invalid else "facet_citation_repairs")
                if invalid:
                    repair = {
                        "invalid_check_ids": invalid,
                        "errors": parsed["errors"],
                        "instruction": "Repair only malformed assessment structure for these IDs. Preserve all already valid facets, including every unknown or contradicted judgment. Do not retry uncertainty until it becomes supported.",
                    }
                else:
                    repair = {
                        "citation_targets": targets,
                        "instruction": "Return ONLY {citation_repairs:[{id:string,facet:string,evidence:[EVIDENCE]}]}. Repair missing or malformed literal references for the listed known:true facets only. Existing known/verdict/reason and every unknown or contradicted facet are immutable. If no citation supports it, leave its evidence empty; do not invent evidence.",
                    }
                messages.extend(
                    [
                        {"role": "assistant", "content": raw if isinstance(raw, str) else ""},
                        {"role": "user", "content": _V10V4_json.dumps(repair, ensure_ascii=False)},
                    ]
                )
            result = parsed["response"]
            accepted, rejected = _V10Review_validate_facet_admission(
                result, proposals, self.problem, self.qa[1]
            )
            conclusive = _V10Review_conclusive_rejection_ids(
                result, proposals, self.problem, self.qa[1]
            )
            self.artifacts["blind_admissions"].append(
                {
                    "qa_hash": self.digest,
                    "check_ids": [p["id"] for p in proposals],
                    "accepted_ids": accepted,
                    "rejected": rejected,
                    "challenge": diagnosis is not None,
                    "conclusive_rejected_ids": conclusive,
                    "candidate_code_or_observations_supplied": False,
                }
            )
            self.artifacts["checks"]["reviews"].append(_V10V4_copy.deepcopy(result))
            return {
                "accepted_ids": accepted,
                "rejected": rejected,
                "conclusive_rejected_ids": conclusive,
            }

        def review(self, env, candidate, proposals, *, additions=False):
            result = super().review(env, candidate, proposals, additions=additions)
            self.candidateReviews[(self.digest, candidate["candidate_id"])] = result
            if candidate is self.best and candidate.get("observations") is not None:
                self.complete_check_coverage(env, candidate, result)
                if self.best is not candidate:
                    # An opinion about the replaced program cannot follow selection.
                    return {
                        **result,
                        "candidate_id": self.best["candidate_id"],
                        "issues": [],
                        "check_objections": [],
                    }
            return result

        def execute_checks(self, env, candidate):
            rows = super().execute_checks(env, candidate)
            reviewed = self.candidateReviews.get((self.digest, candidate["candidate_id"]))
            if rows is not None and candidate is self.best and reviewed:
                self.complete_check_coverage(env, candidate, reviewed)
            return candidate.get("observations")

        def complete_check_coverage(self, env, candidate, reviewed):
            admitted = self.artifacts["checks"]["admitted"]
            active = {p["id"] for p in admitted}
            if (
                candidate.get("observations") is None
                or candidate["qa_hash"] != self.digest
                or any(
                    r["id"] in active and r["status"] != "pass" for r in candidate["observations"]
                )
            ):
                return
            issues = reviewed.get("issues", [])
            identity = (self.digest, candidate["code"], tuple(sorted(i["id"] for i in issues)))
            remaining = max(0, _V10V2_MAX_CHECKS - len(admitted))
            if not issues or not remaining or identity in self.completionSeen:
                return
            self.completionSeen.add(identity)
            self.count("review_check_completions")
            value = self.json_call(
                env,
                _V10V4_COMPLETION_INSTRUCTIONS,
                {
                    **self.context(),
                    "candidate": candidate["code"],
                    "candidate_issues_fallible": issues,
                    "admitted_checks": admitted,
                },
                "review_check_completion",
            )
            existing = {p["id"] for p in self.artifacts["checks"]["proposed"]}
            proposals = self.checks_from(value, limit=min(2, remaining), existing_ids=existing)
            assessment = self.blind_assess(env, proposals)
            before = {p["id"] for p in admitted}
            self.admit(proposals, assessment["accepted_ids"])
            added = [p["id"] for p in self.artifacts["checks"]["admitted"] if p["id"] not in before]
            self.artifacts["check_completions"].append(
                {
                    "candidate_id": candidate["candidate_id"],
                    "qa_hash": self.digest,
                    "issue_ids": [i["id"] for i in issues],
                    "admitted_ids": added,
                }
            )
            self.count("review_check_completion_admitted", len(added))
            if not added:
                return
            preserved = self.best
            for item in self.artifacts["candidates"]:
                if item["eligible"] and item["qa_hash"] == self.digest:
                    rows = super().execute_checks(env, item)
                    if rows is None and item is preserved:
                        self.best = preserved
                        raise _CompletionObservationUnknown()
            # Expansion differs from revocation: an incomparable earlier candidate
            # must not discard checks already passed by the preserved current best.
            self.best = preserved
            admitted = self.artifacts["checks"]["admitted"]
            for item in self.artifacts["candidates"]:
                if (
                    item["eligible"]
                    and item["qa_hash"] == self.digest
                    and item.get("observations") is not None
                    and self.passed(self.best, admitted) < self.passed(item, admitted)
                ):
                    self.best = item
                    item["selection_reason"] = (
                        "expanded_checks_strict_improvement_without_regression"
                    )

        def implement(self, env):
            try:
                return super().implement(env)
            except _CompletionObservationUnknown:
                self.artifacts["status"] = "completion_observation_unknown_preserve_candidate"

        initialize = __init__

    class _V10V4_IntentBridgeV4Clarifier(_V10V3_IntentBridgeV3Clarifier):
        """Bounded citation/protocol recovery and grounded review-check completion."""

        DEFAULT_CONFIG = dict(_V10V3_IntentBridgeV3Clarifier.DEFAULT_CONFIG)

        def localRun(self, env, problem, fixed_qa=None):
            for field, ceiling in self.DEFAULT_CONFIG.items():
                if type(self.config[field]) is not int or not 0 <= self.config[field] <= ceiling:
                    raise ValueError(field + " must be an integer within the fixed default ceiling")
            if self.config["max_candidates"] < 1:
                raise ValueError("max_candidates must allow the initial implementation")
            visible = {"prompt": problem["prompt"], "entry_point": problem["entry_point"]}
            if (
                not isinstance(visible["prompt"], str)
                or not isinstance(visible["entry_point"], str)
                or not visible["entry_point"].isidentifier()
                or _V10V4_keyword.iskeyword(visible["entry_point"])
            ):
                raise ValueError("invalid_visible_task_or_entry_point")
            state = _V10V4__Run(
                dict(self.config),
                _V10V4_copy.deepcopy(self.policy),
                visible,
                conditioned=fixed_qa is not None,
            )
            try:
                return state.execute(env, fixed_qa)
            finally:
                self.artifacts, self.trace = (
                    _V10V4_copy.deepcopy(state.artifacts),
                    _V10V4_copy.deepcopy(state.trace),
                )

    # Frozen source: pilot/intentbridge_v5_20261102/coverage.py
    """Pure candidate-blind coverage protocol; literal citations are not proofs.

No verdict here admits a check, triggers a repair, or selects a program. Callers
must retain independent facet admission and environment-only observations. The
caller also owns the once-per-actual-Q/A-epoch limit: echoed epochs do not create
new authority or authenticate a chronology.
"""

    import copy as _V10Coverage_copy
    import hashlib as _V10Coverage_hashlib
    import json as _V10Coverage_json

    _V10Coverage_MAX_COMPLETION_CHECKS = 2
    _V10Coverage_MAX_OBLIGATIONS = 16
    _V10Coverage__SHARED_CHECK_FIELDS = {"id", "args", "kwargs", "kind", "evidence", "derivation"}
    _V10Coverage__REPORT_FIELDS = {"coverage", "obligations", "checks", "unresolved"}

    def _V10Coverage__json(value):
        return _V10Coverage_json.dumps(
            value, sort_keys=True, ensure_ascii=True, allow_nan=False, separators=(",", ":")
        )

    def _V10Coverage__sha(value):
        return _V10Coverage_hashlib.sha256(_V10Coverage__json(value).encode("utf-8")).hexdigest()

    def _V10Coverage__strings(value, *, maximum=_V10Coverage_MAX_OBLIGATIONS):
        if (
            not isinstance(value, list)
            or len(value) > maximum
            or not all(isinstance(item, str) and item.strip() for item in value)
            or len(set(value)) != len(value)
        ):
            raise ValueError("coverage_nonempty_unique_string_array_required")
        return list(value)

    def _V10Coverage__check_projection(check, problem, question, answer):
        """Project only executable check data and literal evidence, never metadata."""
        if not isinstance(check, dict):
            raise ValueError("coverage_current_check_object_required")
        fields = _V10Coverage__SHARED_CHECK_FIELDS | (
            {"target", "expected"} if check.get("kind") == "exact" else {"property"}
        )
        projected = {
            key: _V10Coverage_copy.deepcopy(check[key])
            for key in fields
            if key in check and key != "derivation"
        }
        projected["derivation"] = _V10Review_BLIND_DERIVATION
        projected["evidence"] = _V10Evidence_resolve_evidence(
            check.get("evidence"), problem, answer, question=question
        )
        return projected

    def _V10Coverage_build_coverage_payload(
        problem, question, answer, admitted_checks, *, qa_hash, qa_epoch
    ):
        # fmt: off
        """Build a whitelist-only payload bound to complete visible Q/A and checks.

    Candidate code, results, reviews, briefs and source/task identities are not
    accepted payload fields. Literal input data and visible text stay intact.
    An arbitrary caller-supplied Q/A hash is never treated as authority.
    """
        # fmt: on
        visible = {"prompt": problem["prompt"], "entry_point": problem["entry_point"]}
        if (
            not all(
                isinstance(item, str)
                for item in (visible["prompt"], visible["entry_point"], question, answer)
            )
            or type(qa_epoch) is not int
            or qa_epoch < 0
        ):
            raise ValueError("coverage_visible_context_invalid")
        expected_hash = _V10V2_qa_hash(visible, question, answer)
        if not isinstance(qa_hash, str) or qa_hash != expected_hash:
            raise ValueError("coverage_qa_hash_mismatch")
        if not isinstance(admitted_checks, list) or len(admitted_checks) > _V10V2_MAX_CHECKS:
            raise ValueError("coverage_current_checks_invalid")
        current = [
            _V10Coverage__check_projection(check, visible, question, answer)
            for check in admitted_checks
        ]
        good, rejected = _V10Protocol_validate_checks(
            {"checks": current}, visible, answer, limit=_V10V2_MAX_CHECKS
        )
        if rejected or len(good) != len(current):
            raise ValueError("coverage_current_checks_invalid")
        checks_hash = _V10Coverage__sha(current)
        binding = {"qa_hash": expected_hash, "qa_epoch": qa_epoch, "checks_sha256": checks_hash}
        binding["coverage_hash"] = _V10Coverage__sha(
            {
                "task": visible,
                "actual_question": question,
                "actual_answer": answer,
                "admitted_checks": current,
                **binding,
            }
        )
        return {
            "task": visible,
            "actual_question": question,
            "actual_answer": answer,
            "admitted_checks": current,
            "binding": binding,
            "evidence_catalog": _V10Evidence_build_evidence_catalog(
                visible, answer, question=question
            ),
        }

    def _V10Coverage_validate_coverage_report(
        value,
        admitted_checks,
        problem,
        answer,
        *,
        question,
        qa_hash,
        qa_epoch,
        limit=_V10Coverage_MAX_COMPLETION_CHECKS,
    ):
        # fmt: off
        """Fail closed on malformed/stale reports; never infer missing expectations.

    ``checks`` contains only mechanically valid proposals, not admitted checks.
    Semantic entailment remains a separate independent decision. Unknown and
    adequate verdicts always return an empty proposal list, even if a model
    supplied invented values. A gap must identify a cited uncovered obligation.
    """
        # fmt: on
        result = {
            "coverage": "unknown",
            "obligations": [],
            "checks": [],
            "unresolved": [],
            "binding": {},
            "errors": [],
        }
        try:
            if type(limit) is not int or not 0 <= limit <= _V10Coverage_MAX_COMPLETION_CHECKS:
                raise ValueError("coverage_check_limit_invalid")
            payload = _V10Coverage_build_coverage_payload(
                problem, question, answer, admitted_checks, qa_hash=qa_hash, qa_epoch=qa_epoch
            )
            result["binding"] = payload["binding"]
            if (
                not isinstance(value, dict)
                or not _V10Coverage__REPORT_FIELDS <= set(value)
                or set(value) - _V10Coverage__REPORT_FIELDS - {"binding"}
            ):
                raise ValueError("coverage_report_fields_invalid")
            # The engine owns the binding. Models need not copy opaque hashes; an
            # explicitly supplied stale/tampered binding is still never accepted.
            if "binding" in value and _V10Coverage__json(value["binding"]) != _V10Coverage__json(
                payload["binding"]
            ):
                raise ValueError("coverage_report_binding_mismatch")
            verdict = value["coverage"]
            if not isinstance(verdict, str) or verdict not in {"adequate", "gap", "unknown"}:
                raise ValueError("coverage_verdict_invalid")
            unresolved = _V10Coverage__strings(value["unresolved"])
            obligations = value["obligations"]
            if not isinstance(obligations, list) or len(obligations) > _V10Coverage_MAX_OBLIGATIONS:
                raise ValueError("coverage_obligations_invalid")
            active = {check["id"] for check in payload["admitted_checks"]}
            clean = []
            for item in obligations:
                if (
                    not isinstance(item, dict)
                    or set(item) != {"requirement", "evidence", "covered_by"}
                    or not isinstance(item["requirement"], str)
                    or not item["requirement"].strip()
                ):
                    raise ValueError("coverage_obligation_fields_invalid")
                ids = _V10Coverage__strings(item["covered_by"], maximum=_V10V2_MAX_CHECKS)
                if any(ident not in active for ident in ids):
                    raise ValueError("coverage_unknown_covered_by_id")
                clean.append(
                    {
                        "requirement": item["requirement"],
                        "evidence": _V10Evidence_resolve_evidence(
                            item["evidence"], payload["task"], answer, question=question
                        ),
                        "covered_by": ids,
                    }
                )
            if verdict != "unknown" and not clean:
                raise ValueError("coverage_cited_obligation_required")
            if verdict == "adequate" and any(not item["covered_by"] for item in clean):
                raise ValueError("coverage_adequate_has_uncovered_obligation")
            if verdict == "gap" and not any(not item["covered_by"] for item in clean):
                raise ValueError("coverage_gap_has_no_uncovered_obligation")
            proposed = value["checks"]
            if not isinstance(proposed, list):
                raise ValueError("coverage_checks_array_required")
            result.update(coverage=verdict, obligations=clean, unresolved=unresolved)
            if verdict != "gap":
                if proposed:
                    result["errors"].append("coverage_checks_not_allowed_for_" + verdict)
                return result
            remaining = min(limit, max(0, _V10V2_MAX_CHECKS - len(admitted_checks)))
            canonical = []
            for check in proposed:
                if not isinstance(check, dict):
                    raise ValueError("coverage_proposal_object_required")
                item = _V10Coverage_copy.deepcopy(check)
                item["evidence"] = _V10Evidence_resolve_evidence(
                    item.get("evidence"), payload["task"], answer, question=question
                )
                canonical.append(item)
            good, rejected = _V10Protocol_validate_checks(
                {"checks": canonical}, payload["task"], answer, existing_ids=active, limit=remaining
            )
            if rejected or len(good) != len(canonical):
                raise ValueError("coverage_proposed_checks_invalid")
            result["checks"] = good
            return result
        except (AttributeError, KeyError, TypeError, ValueError, RecursionError) as error:
            # Rejected model objects are not recycled as new context or authority.
            result.update(coverage="unknown", obligations=[], checks=[], unresolved=[])
            code = str(error) if isinstance(error, ValueError) else "coverage_report_invalid"
            result["errors"].append(code)
            return result

    # Frozen source: pilot/intentbridge_v5_20261102/decisions.py
    """Pure pre-question decision profiles over the complete visible task.

Literal evidence proves that text occurs in the prompt, not that a model's
interpretation follows from it.  These helpers neither infer a contract nor
execute code.  They keep question selection separate from tentative programs,
and never replace the complete task with a structured profile.
"""

    _V10Decisions_PROFILE_FIELDS = ("known_requirements", "main_unknowns", "other_unknowns")
    _V10Decisions__FACT_FIELDS = {"fact", "evidence"}
    _V10Decisions__DECISION_FIELDS = {"decision", "why_material", "evidence"}

    def _V10Decisions__error(path, code):
        return {"path": path, "code": code}

    def _V10Decisions__visible_task(problem):
        if not isinstance(problem, dict):
            raise ValueError("decision_visible_task_object_required")
        visible = {field: problem.get(field) for field in ("prompt", "entry_point")}
        if not all(isinstance(value, str) for value in visible.values()):
            raise ValueError("decision_visible_prompt_and_entry_point_required")
        return visible

    def _V10Decisions__prompt_evidence(value, problem, path):
        """Use the v3 exact-text validator with prompt as the sole authority."""
        if isinstance(value, list):
            for index, item in enumerate(value):
                if isinstance(item, dict) and item.get("source") != "prompt":
                    raise EvidenceValidationError(
                        [
                            _V10Decisions__error(
                                path + "[" + str(index) + "].source",
                                "decision_prompt_evidence_required",
                            )
                        ]
                    )
        return _V10Evidence_resolve_evidence(value, problem, "", path=path)

    def _V10Decisions_normalize_decision_profile(value, problem):
        # fmt: off
        """Retain independently well-formed, prompt-cited model claims.

    The three output lists contain only whitelisted fields.  Invalid neighbors
    are dropped locally, without rescuing a fact with a fabricated citation.
    Unknowns remain model hypotheses; valid citations do not establish their
    consequence or importance.  An empty unknown list is valid for an explicit
    task, and an invalid/empty profile never changes the original task.

    ``errors`` is accepted as an ignored field when rechecking this function's
    own output.  Arbitrary caller diagnostics are never copied into the result.
    """
        # fmt: on
        visible = _V10Decisions__visible_task(problem)
        result = {field: [] for field in _V10Decisions_PROFILE_FIELDS}
        errors = result["errors"] = []
        if not isinstance(value, dict):
            errors.append(_V10Decisions__error("$", "decision_profile_object_required"))
            return result
        if set(value) - set(_V10Decisions_PROFILE_FIELDS) - {"errors"}:
            errors.append(_V10Decisions__error("$", "decision_profile_unexpected_fields"))
        for field in _V10Decisions_PROFILE_FIELDS:
            if field not in value:
                errors.append(_V10Decisions__error(field, "decision_profile_field_missing"))
                continue
            items = value[field]
            if not isinstance(items, list):
                errors.append(_V10Decisions__error(field, "decision_profile_array_required"))
                continue
            for index, item in enumerate(items):
                path = field + "[" + str(index) + "]"
                if field == "other_unknowns":
                    if isinstance(item, str) and item.strip():
                        result[field].append(item)
                    else:
                        errors.append(_V10Decisions__error(path, "decision_unknown_text_required"))
                    continue
                expected = (
                    _V10Decisions__FACT_FIELDS
                    if field == "known_requirements"
                    else _V10Decisions__DECISION_FIELDS
                )
                if not isinstance(item, dict) or set(item) != expected:
                    errors.append(_V10Decisions__error(path, "decision_item_fields_invalid"))
                    continue
                text_fields = (
                    ("fact",) if field == "known_requirements" else ("decision", "why_material")
                )
                before = len(errors)
                for text_field in text_fields:
                    if not isinstance(item[text_field], str) or not item[text_field].strip():
                        errors.append(
                            _V10Decisions__error(
                                path + "." + text_field, "decision_nonempty_text_required"
                            )
                        )
                canonical = None
                try:
                    canonical = _V10Decisions__prompt_evidence(
                        item["evidence"], visible, path + ".evidence"
                    )
                except EvidenceValidationError as error:
                    errors.extend(error.errors)
                if len(errors) == before:
                    accepted = {key: item[key] for key in text_fields}
                    accepted["evidence"] = canonical
                    result[field].append(accepted)
        return result

    def _V10Decisions_build_question_payload(problem, normalized_profile):
        # fmt: off
        """Project full visible task and a rechecked fallible decision profile.

    No tentative program, worlds, witness, examples, candidate, assumed
    signature or metadata field from a raw proposal is a supported payload
    field.  The visible prompt itself stays byte-for-byte intact, including any
    code, signature or examples actually supplied by the user.  Rechecking
    prevents caller mutation or an unnormalized profile bypassing projection.
    """
        # fmt: on
        visible = _V10Decisions__visible_task(problem)
        checked = _V10Decisions_normalize_decision_profile(normalized_profile, visible)
        return {
            "task": visible,
            "fallible_decision_profile": {
                field: checked[field] for field in _V10Decisions_PROFILE_FIELDS
            },
            "profile_citations_are_not_proof": True,
        }

    # Frozen source: pilot/intentbridge_v5_20261102/algorithm.py
    """Main-contract discovery and candidate-blind visible coverage recovery.

This independent revision leaves all prior paid/frozen sources untouched. It
cannot obtain missing intent from hidden materials or certify model judgments.
"""

    import copy as _V10V5_copy
    import keyword as _V10V5_keyword

    _V10V5_DEFAULT_POLICY = _V10V5_copy.deepcopy(_V10V4_DEFAULT_POLICY)

    _V10V5_DECISION_INSTRUCTIONS = (
        _V10V2_GROUNDING
        + """Inspect the complete visible task
BEFORE proposing any implementation. Identify which main behavioral decisions
are already stated and which remain unknown on normal legal inputs. Do not
write code, candidate programs, worlds, assumed signatures, candidate outputs,
or a guessed solution. A callable name or category convention is not a rule.
Give no automatic priority to signature, return type, or edge cases. Distinguish
a missing operation/recurrence/stopping rule from a missing interface detail.
Return JSON {known_requirements:[{fact:string,evidence:[{source:'prompt',quote:EXACT_TEXT}]}],
main_unknowns:[{decision:string,why_material:string,evidence:[{source:'prompt',quote:EXACT_TEXT}]}],
other_unknowns:[string]}. A quote anchors a fallible analysis, not a proof.
An explicit task may have main_unknowns:[]; do not invent uncertainty.
"""
    )

    _V10V5_QUESTION_INSTRUCTIONS = (
        _V10V2_GROUNDING
        + """Choose ONE neutral clarification
about the missing fact with the largest consequence for the main behavior.
Independently read the full task: the decision profile is fallible working
analysis. No tentative implementation is provided or authoritative. If the
normal operation or general rule is unknown, obtain that rule rather than only
its return shape, argument count, or an isolated output shared by many rules.
Use a complete illustrative input when helpful; do not assert that an invented
function call, arity or input shape is already legal. Ask an open question when
the alternatives are not known to be exhaustive. Do not embed a guessed
mechanism and ask only a secondary detail. Do not stack unrelated arity,
default, type and boundary questions. A single coherent behavioral rule may
need related explanation; there is no word-count or punctuation heuristic.
When the main rule is explicit, ask only a material remaining uncertainty or a
task-specific confirmation. Do not repeat known facts or request algorithms,
hidden requirements or tests. Return JSON {question:string,target:string,
mode:'uncertainty'|'confirmation'|'none',reason:string}. mode:none requires an
empty question. A partial actual answer will not settle unrelated choices.
"""
    )

    _V10V5_COVERAGE_INSTRUCTIONS = (
        _V10V2_GROUNDING
        + _V10V3_REFERENCE_INSTRUCTIONS
        + _V10Checks_CHECK_SEMANTICS_INSTRUCTIONS
        + _V10V2_TYPED_INSTRUCTIONS
        + _V10V3_CHECK_OBJECT_SCHEMA
        + """Audit the coverage of the CURRENT
visible checks without seeing any candidate, observations, or reviewer claims.
Identify the main computation actually specified by the full task and literal
answer. Does a current check exercise it, or only one shape, an easy/fixed-point
example, or a secondary detail? An exact example need not distinguish the main
rule from a wrong implementation. Do not invent requirements to increase test
count. A shape-only check can be sufficient when shape is the full task.
If a main obligation is unknown or contradictory, preserve that uncertainty.
For a concrete uncovered rule, propose at most TWO new checks entailed by the
visible source, with fresh IDs. Never derive expected values from a program.
Every proposal still requires separate independent admission and execution.
Return JSON {coverage:'adequate'|'gap'|'unknown',obligations:[{requirement:string,
evidence:[EVIDENCE],covered_by:[CURRENT_CHECK_ID]}],checks:[CHECK],unresolved:[string]}.
An uncovered obligation uses covered_by:[]. adequate and unknown use checks:[].
This report cannot authorize a repair or establish program correctness.
"""
    )

    class _V10V5__Run(_V10V4__Run):
        def __init__(self, config, policy, problem, *, conditioned=False):
            super().initialize(config, policy, problem, conditioned=conditioned)
            self.artifacts["variant"] = "intentbridge_v5_main_contract_coverage"
            self.artifacts.update(decision_profile={}, main_rule_coverage=[])
            self.coverageSeen = set()
            self.artifacts["mechanisms"].update(
                main_rule_coverage_calls=0,
                main_rule_coverage_admitted=0,
                main_rule_coverage_unknown=0,
            )

        def plan_and_ask(self, env):
            value = self.json_call(
                env,
                _V10V5_DECISION_INSTRUCTIONS + self.guidance("plan_guidance"),
                {"task": self.problem},
                "main_decision_discovery",
            )
            profile = _V10Decisions_normalize_decision_profile(value, self.problem)
            self.artifacts["decision_profile"] = _V10V5_copy.deepcopy(profile)
            self.artifacts["proposal"] = _V10V5_copy.deepcopy(profile)
            if not env.can_ask():
                return

            def schema(value):
                if (
                    not isinstance(value.get("question"), str)
                    or not isinstance(value.get("target"), str)
                    or not isinstance(value.get("reason"), str)
                    or value.get("mode") not in {"uncertainty", "confirmation", "none"}
                ):
                    raise ValueError("question_schema_invalid")
                if value["mode"] == "none" and value["question"].strip():
                    raise ValueError("question_none_mode_requires_empty_text")
                return value

            meta = self.json_call(
                env,
                _V10V5_QUESTION_INSTRUCTIONS + self.guidance("plan_guidance"),
                _V10Decisions_build_question_payload(self.problem, profile),
                "question_selection",
                schema,
            )
            self.artifacts["question_meta"] = _V10V5_copy.deepcopy(meta or {})
            question = meta.get("question", "") if meta else ""
            if not question.strip() or self.asked or not env.can_ask():
                return
            self.count("question_attempted")
            self.set_qa(question, "", status="attempted")
            try:
                answer = env.ask_human(question)
            except _V10V2_TooManyQuestionException:
                self.artifacts["qa_events"][-1]["status"] = "environment_refused"
                return
            if not isinstance(answer, str):
                raise TypeError("actual_answer_must_be_string")
            self.qa = (question, answer)
            self.digest = _V10V2_qa_hash(self.problem, question, answer)
            self.artifacts["qa_events"][-1].update(
                answer=answer, status="completed", qa_hash=self.digest
            )

        def complete_check_coverage(self, env, candidate, reviewed):
            # Preserve v4's issue-specific path. New coverage discovery fills the
            # otherwise untouched issues=[] branch, not a second opinion on code.
            if reviewed.get("issues"):
                return super().complete_check_coverage(env, candidate, reviewed)
            admitted = self.artifacts["checks"]["admitted"]
            active = {p["id"] for p in admitted}
            key = (self.epoch, self.digest)
            remaining = max(0, _V10V2_MAX_CHECKS - len(admitted))
            if (
                candidate is not self.best
                or candidate["qa_hash"] != self.digest
                or candidate.get("observations") is None
                or not remaining
                or key in self.coverageSeen
                or any(
                    r["id"] in active and r["status"] != "pass" for r in candidate["observations"]
                )
            ):
                return
            self.coverageSeen.add(key)
            self.count("main_rule_coverage_calls")
            payload = _V10Coverage_build_coverage_payload(
                self.problem,
                self.qa[0],
                self.qa[1],
                admitted,
                qa_hash=self.digest,
                qa_epoch=self.epoch,
            )

            def schema(value):
                if value.get("coverage") not in {"adequate", "gap", "unknown"} or not all(
                    isinstance(value.get(k), list) for k in ("obligations", "checks", "unresolved")
                ):
                    raise ValueError("main_rule_coverage_schema_invalid")
                return value

            raw = self.json_call(
                env, _V10V5_COVERAGE_INSTRUCTIONS, payload, "main_rule_coverage", schema
            )
            report = _V10Coverage_validate_coverage_report(
                raw,
                admitted,
                self.problem,
                self.qa[1],
                question=self.qa[0],
                qa_hash=self.digest,
                qa_epoch=self.epoch,
                limit=min(2, remaining),
            )
            report.update(
                candidate_id=candidate["candidate_id"],
                admitted_ids=[],
                candidate_code_or_observations_supplied=False,
            )
            self.artifacts["main_rule_coverage"].append(_V10V5_copy.deepcopy(report))
            if report["coverage"] == "unknown":
                self.count("main_rule_coverage_unknown")
            existing = {p["id"] for p in self.artifacts["checks"]["proposed"]}
            proposals = self.checks_from(
                {"checks": report["checks"]}, limit=min(2, remaining), existing_ids=existing
            )
            assessment = self.blind_assess(env, proposals)
            self.admit(proposals, assessment["accepted_ids"])
            added = [p["id"] for p in self.artifacts["checks"]["admitted"] if p["id"] not in active]
            self.artifacts["main_rule_coverage"][-1]["admitted_ids"] = added
            self.count("main_rule_coverage_admitted", len(added))
            if not added:
                return
            preserved = self.best
            for item in self.artifacts["candidates"]:
                if item["eligible"] and item["qa_hash"] == self.digest:
                    rows = _V10V3__Run.execute_checks(self, env, item)
                    if rows is None and item is preserved:
                        self.best = preserved
                        raise _CompletionObservationUnknown()
            self.best = preserved
            admitted = self.artifacts["checks"]["admitted"]
            for item in self.artifacts["candidates"]:
                if (
                    item["eligible"]
                    and item["qa_hash"] == self.digest
                    and item.get("observations") is not None
                    and self.passed(self.best, admitted) < self.passed(item, admitted)
                ):
                    self.best = item
                    item["selection_reason"] = (
                        "main_rule_checks_strict_improvement_without_regression"
                    )

        def implement(self, env):
            super().implement(env)
            records = self.artifacts["main_rule_coverage"]
            if (
                records
                and not records[-1]["admitted_ids"]
                and records[-1]["coverage"] != "adequate"
                and self.artifacts["status"]
                in {"visible_checks_satisfied", "no_grounded_checks_preserve_candidate"}
            ):
                self.artifacts["status"] = "main_rule_coverage_unresolved_preserve_candidate"

        initialize = __init__

    class _V10V5_IntentBridgeV5Clarifier(_V10V4_IntentBridgeV4Clarifier):
        """Code-free question discovery and bounded main-rule coverage checks."""

        DEFAULT_CONFIG = dict(_V10V4_IntentBridgeV4Clarifier.DEFAULT_CONFIG)

        def localRun(self, env, problem, fixed_qa=None):
            for field, ceiling in self.DEFAULT_CONFIG.items():
                if type(self.config[field]) is not int or not 0 <= self.config[field] <= ceiling:
                    raise ValueError(field + " must be an integer within the fixed default ceiling")
            if self.config["max_candidates"] < 1:
                raise ValueError("max_candidates must allow the initial implementation")
            visible = {"prompt": problem["prompt"], "entry_point": problem["entry_point"]}
            if (
                not isinstance(visible["prompt"], str)
                or not isinstance(visible["entry_point"], str)
                or not visible["entry_point"].isidentifier()
                or _V10V5_keyword.iskeyword(visible["entry_point"])
            ):
                raise ValueError("invalid_visible_task_or_entry_point")
            state = _V10V5__Run(
                dict(self.config),
                _V10V5_copy.deepcopy(self.policy),
                visible,
                conditioned=fixed_qa is not None,
            )
            try:
                return state.execute(env, fixed_qa)
            finally:
                self.artifacts, self.trace = (
                    _V10V5_copy.deepcopy(state.artifacts),
                    _V10V5_copy.deepcopy(state.trace),
                )

    # Frozen source: pilot/intentbridge_question_learning_20261102/algorithm.py
    """Independent visible-only exactly-one-question protocol over frozen v5.

This is a protocol revision, not a trained question policy or evidence of
information gain. Failed or unavailable interactions remain incomplete.
"""

    import copy as _V10Question_copy
    import keyword as _V10Question_keyword

    _V10Question_DEFAULT_POLICY = _V10Question_copy.deepcopy(_V10V5_DEFAULT_POLICY)

    _V10Question_QUESTION_INSTRUCTIONS = (
        _V10V2_GROUNDING
        + """Ask exactly ONE neutral,
task-specific clarification. Identify the visible uncertainty whose resolution
would most change legal program behavior. The decision profile is fallible;
independently read the complete task. No candidate code or hidden information is
provided. Do not hard-code a question category or presume a signature, output,
mechanism or exhaustive alternatives not established by the task. Ask for one
specific requirement; do not bundle independent facts or request every missing
requirement, an implementation, hidden tests, or a reference answer. Prefer an
open question when the alternatives cannot be established. If no material
unknown is identified, ask one precise task-specific confirmation of a stated
behavior without inventing a missing fact. Such confirmation may add no new
information: mandatory asking is not proof of usefulness. Do not invent a
generic question merely to satisfy this protocol.
Return JSON {question:NONEMPTY_STRING,target:NONEMPTY_STRING,
mode:'uncertainty'|'confirmation',reason:NONEMPTY_STRING}. mode:none and blank
questions are invalid. Describe the target decision and why a substantive
answer could matter; do not claim that asking guarantees that answer.
"""
    )

    class QuestionProtocolIncomplete(RuntimeError):
        """The required actual clarification could not be completed."""

    class _V10Question__Run(_V10V5__Run):
        def __init__(self, config, policy, problem, *, conditioned=False):
            super().initialize(config, policy, problem, conditioned=conditioned)
            self.artifacts["variant"] = "intentbridge_mandatory_single_question"
            self.artifacts["question_protocol"] = {
                "required_actual_questions": 0 if conditioned else 1,
                "conditioned_diagnostic_excluded": conditioned,
                "actual_invocations": 0,
                "completed_interactions": 0,
                "status": "conditioned_diagnostic_excluded" if conditioned else "pending",
                "information_gain_guaranteed": False,
            }

        def incomplete(self, reason):
            self.artifacts["question_protocol"]["status"] = reason
            self.artifacts["status"] = "question_protocol_incomplete"
            self.record(phase="question_protocol", status="incomplete", reason=reason)
            raise QuestionProtocolIncomplete(reason)

        def plan_and_ask(self, env):
            protocol = self.artifacts["question_protocol"]
            if self.asked or protocol["actual_invocations"]:
                self.incomplete("duplicate_question_attempt_forbidden")
            if not env.can_ask():
                self.incomplete("environment_cannot_ask")

            value = self.json_call(
                env,
                _V10V5_DECISION_INSTRUCTIONS + self.guidance("plan_guidance"),
                {"task": self.problem},
                "main_decision_discovery",
            )
            profile = _V10Decisions_normalize_decision_profile(value, self.problem)
            self.artifacts["decision_profile"] = _V10Question_copy.deepcopy(profile)
            self.artifacts["proposal"] = _V10Question_copy.deepcopy(profile)

            def schema(value):
                if (
                    not isinstance(value, dict)
                    or value.get("mode") not in {"uncertainty", "confirmation"}
                    or any(
                        not isinstance(value.get(field), str) or not value[field].strip()
                        for field in ("question", "target", "reason")
                    )
                ):
                    raise ValueError(
                        "mandatory_question_requires_nonempty_question_target_reason_and_valid_mode"
                    )
                return value

            meta = self.json_call(
                env,
                _V10Question_QUESTION_INSTRUCTIONS + self.guidance("plan_guidance"),
                _V10Decisions_build_question_payload(self.problem, profile),
                "question_selection",
                schema,
            )
            self.artifacts["question_meta"] = _V10Question_copy.deepcopy(meta or {})
            if meta is None:
                self.incomplete("question_format_recovery_exhausted")
            if not env.can_ask():
                self.incomplete("environment_cannot_ask_after_question_selection")

            question = meta["question"]
            self.count("question_attempted")
            self.set_qa(question, "", status="attempted")
            protocol.update(actual_invocations=1, status="attempted")
            try:
                answer = env.ask_human(question)
            except _V10V2_TooManyQuestionException as error:
                self.artifacts["qa_events"][-1]["status"] = "environment_refused"
                self.artifacts["question_protocol"]["status"] = "environment_refused"
                self.artifacts["status"] = "question_protocol_incomplete"
                raise QuestionProtocolIncomplete("environment_refused") from error
            # Provider/configuration exceptions escape unchanged for checkpointed
            # recovery. Never manufacture an answer or repeat this interaction here.
            if not isinstance(answer, str):
                self.artifacts["qa_events"][-1]["status"] = "invalid_answer_type"
                self.incomplete("actual_answer_must_be_string")
            self.qa = (question, answer)
            self.digest = _V10V2_qa_hash(self.problem, question, answer)
            self.artifacts["qa_events"][-1].update(
                answer=answer, status="completed", qa_hash=self.digest
            )
            protocol.update(completed_interactions=1, status="completed")

        def execute(self, env, fixed_qa=None):
            code = super().execute(env, fixed_qa)
            # The inherited official-limit handler can finish before plan_and_ask
            # completes. Such a trajectory must not silently enter the completed
            # always-ask denominator as a zero-question code submission.
            if fixed_qa is None:
                protocol = self.artifacts["question_protocol"]
                if protocol["actual_invocations"] != 1 or protocol["completed_interactions"] != 1:
                    self.incomplete("required_actual_question_not_completed")
            return code

        initialize = __init__

    class _V10Question_IntentBridgeQuestionLearningClarifier(_V10V5_IntentBridgeV5Clarifier):
        """One actual question per completed unconditioned task; no IG guarantee."""

        def localRun(self, env, problem, fixed_qa=None):
            for field, ceiling in self.DEFAULT_CONFIG.items():
                if type(self.config[field]) is not int or not 0 <= self.config[field] <= ceiling:
                    raise ValueError(field + " must be an integer within the fixed default ceiling")
            if self.config["max_candidates"] < 1:
                raise ValueError("max_candidates must allow the initial implementation")
            visible = {"prompt": problem["prompt"], "entry_point": problem["entry_point"]}
            if (
                not isinstance(visible["prompt"], str)
                or not isinstance(visible["entry_point"], str)
                or not visible["entry_point"].isidentifier()
                or _V10Question_keyword.iskeyword(visible["entry_point"])
            ):
                raise ValueError("invalid_visible_task_or_entry_point")
            state = _V10Question__Run(
                dict(self.config),
                _V10Question_copy.deepcopy(self.policy),
                visible,
                conditioned=fixed_qa is not None,
            )
            try:
                return state.execute(env, fixed_qa)
            finally:
                self.artifacts, self.trace = (
                    _V10Question_copy.deepcopy(state.artifacts),
                    _V10Question_copy.deepcopy(state.trace),
                )

    # Frozen source: pilot/intentbridge_pass1_20261102/visible_examples.py
    """Literal visible examples become fallible check proposals, never an oracle.

Only the complete visible prompt, supplied entry point and actual answer enter.
No candidate, dataset identity or code is loaded or run. Each result still
requires the ordinary independent admission and execution stages.
"""

    import ast as _V10Visible_ast
    import copy as _V10Visible_copy
    import doctest as _V10Visible_doctest
    import hashlib as _V10Visible_hashlib
    import json as _V10Visible_json
    import math as _V10Visible_math
    import re as _V10Visible_re

    _V10Visible_DERIVATION = (
        "mechanical_visible_literal_example_v1; exact source syntax only; "
        "independent visible-evidence admission is still required"
    )

    class LiteralExampleError(ValueError):
        pass

    def _V10Visible__literal(node):
        """A strict subset of literal_eval, preserving ordinary Python data types."""
        if isinstance(node, _V10Visible_ast.Constant):
            value = _V10Visible_ast.literal_eval(node)
            if value is not None and type(value) not in {bool, int, float, str}:
                raise LiteralExampleError("unsupported_literal_type")
        elif isinstance(node, _V10Visible_ast.UnaryOp) and isinstance(
            node.op, (_V10Visible_ast.UAdd, _V10Visible_ast.USub)
        ):
            if not isinstance(node.operand, _V10Visible_ast.Constant) or type(
                node.operand.value
            ) not in {int, float}:
                raise LiteralExampleError("nonliteral_unary_operand")
            value = _V10Visible_ast.literal_eval(node)
        elif isinstance(node, (_V10Visible_ast.List, _V10Visible_ast.Tuple)):
            for child in node.elts:
                _V10Visible__literal(child)
            value = _V10Visible_ast.literal_eval(node)
        elif isinstance(node, _V10Visible_ast.Dict):
            keys = []
            for key, item in zip(node.keys, node.values, strict=False):
                if key is None:
                    raise LiteralExampleError("dictionary_expansion_not_literal")
                decoded = _V10Visible__literal(key)
                try:
                    hash(decoded)
                    if decoded in keys:
                        raise LiteralExampleError("duplicate_or_colliding_dictionary_key")
                except TypeError as error:
                    raise LiteralExampleError("unhashable_dictionary_key") from error
                keys.append(decoded)
                _V10Visible__literal(item)
            value = _V10Visible_ast.literal_eval(node)
        else:
            raise LiteralExampleError("computed_expression_not_literal")
        if type(value) is float and not _V10Visible_math.isfinite(value):
            raise LiteralExampleError("nonfinite_number_not_supported")
        return value

    def _V10Visible__typed(value):
        if value is None:
            return {"type": "none"}
        if type(value) in {bool, int, float, str}:
            return {"type": _IBTypeName(value), "value": value}
        if type(value) in {list, tuple}:
            return {
                "type": _IBTypeName(value),
                "items": [_V10Visible__typed(item) for item in value],
            }
        if type(value) is dict:
            return {
                "type": "dict",
                "items": [
                    {"key": _V10Visible__typed(key), "value": _V10Visible__typed(item)}
                    for key, item in value.items()
                ],
            }
        raise LiteralExampleError("unsupported_typed_value")

    def _V10Visible__call(node, entry_point):
        if (
            not isinstance(node, _V10Visible_ast.Call)
            or not isinstance(node.func, _V10Visible_ast.Name)
            or node.func.id != entry_point
        ):
            raise LiteralExampleError("not_direct_supplied_entry_point")
        if any(isinstance(item, _V10Visible_ast.Starred) for item in node.args):
            raise LiteralExampleError("starred_argument_not_literal")
        names = [item.arg for item in node.keywords]
        if None in names or len(names) != len(set(names)):
            raise LiteralExampleError("expanded_or_duplicate_keyword")
        return (
            [_V10Visible__typed(_V10Visible__literal(item)) for item in node.args],
            {
                item.arg: _V10Visible__typed(_V10Visible__literal(item.value))
                for item in node.keywords
            },
        )

    def _V10Visible__offsets(text):
        offsets, total = [], 0
        for line in text.splitlines(keepends=True):
            offsets.append(total)
            total += len(line)
        offsets.append(total)
        return offsets

    def _V10Visible__node_span(text, node):
        offsets = _V10Visible__offsets(text)
        # AST columns count UTF-8 bytes, whereas Python string offsets count chars.
        lines = text.splitlines(keepends=True)

        def position(lineno, byte_column):
            prefix = lines[lineno - 1].encode("utf-8")[:byte_column].decode("utf-8")
            return offsets[lineno - 1] + len(prefix)

        return position(node.lineno, node.col_offset), position(
            node.end_lineno, node.end_col_offset
        )

    def _V10Visible__comparison(node, entry_point):
        if (
            not isinstance(node, _V10Visible_ast.Compare)
            or len(node.ops) != 1
            or not isinstance(node.ops[0], _V10Visible_ast.Eq)
        ):
            raise LiteralExampleError("single_equality_required")
        left, right = node.left, node.comparators[0]
        if isinstance(left, _V10Visible_ast.Call):
            args, kwargs = _V10Visible__call(left, entry_point)
            expected = _V10Visible__typed(_V10Visible__literal(right))
        elif isinstance(right, _V10Visible_ast.Call):
            args, kwargs = _V10Visible__call(right, entry_point)
            expected = _V10Visible__typed(_V10Visible__literal(left))
        else:
            raise LiteralExampleError("equality_has_no_direct_call")
        return args, kwargs, expected

    def _V10Visible__data_ranges(fragment, tree):
        """Exclude ordinary string data while retaining function docstring examples."""
        docstrings = set()
        for owner in _V10Visible_ast.walk(tree):
            if (
                isinstance(
                    owner,
                    (
                        _V10Visible_ast.FunctionDef,
                        _V10Visible_ast.AsyncFunctionDef,
                        _V10Visible_ast.ClassDef,
                    ),
                )
                and owner.body
            ):
                first = owner.body[0]
                if (
                    isinstance(first, _V10Visible_ast.Expr)
                    and isinstance(first.value, _V10Visible_ast.Constant)
                    and isinstance(first.value.value, str)
                ):
                    docstrings.add(id(first.value))
        ranges = []
        for node in _V10Visible_ast.walk(tree):
            if (
                isinstance(node, _V10Visible_ast.Constant)
                and isinstance(node.value, (str, bytes))
                and id(node) not in docstrings
            ) or isinstance(node, _V10Visible_ast.JoinedStr):
                ranges.append(_V10Visible__node_span(fragment, node))
        return ranges

    def _V10Visible_extract_visible_examples(problem, answer, *, limit=6):
        # fmt: off
        """Return {checks, skipped}; neither admission nor program execution occurs.

    Supported surfaces are Python assert/equality statements, direct doctest
    calls with literal repr output, and bounded call=literal/arrow mappings.
    Unsupported prose, expressions and types are left unconverted. Contradictory
    examples remain separate proposals for the existing independent reviewer.
    """
        # fmt: on
        prompt, entry_point = problem["prompt"], problem["entry_point"]
        if (
            not isinstance(prompt, str)
            or not isinstance(answer, str)
            or not isinstance(entry_point, str)
            or not entry_point.isidentifier()
        ):
            raise ValueError("visible_prompt_answer_and_entry_point_required")
        if type(limit) is not int or limit < 0:
            raise ValueError("example_limit_must_be_nonnegative_integer")
        checks, skipped, indexed, attempted = [], [], {}, set()

        def skip(source, start, end, reason):
            key = (source, start, end, reason)
            if key not in attempted:
                skipped.append({"source": source, "start": start, "end": end, "reason": reason})
                attempted.add(key)

        def add(parts, source, text, start, end, surface):
            args, kwargs, expected = parts
            quote = text[start:end]
            if not quote.strip():
                return
            # Keyword order can be observed by a **kwargs implementation; do not
            # collapse calls whose keyword insertion order differs.
            identity = _V10Visible_json.dumps(
                [args, list(kwargs.items()), expected, "return"],
                sort_keys=True,
                ensure_ascii=False,
                allow_nan=False,
                separators=(",", ":"),
            )
            reference = {"source": source, "quote": quote}
            if identity in indexed:
                existing = checks[indexed[identity]]
                if reference not in existing["evidence"]:
                    existing["evidence"].append(reference)
                return
            if len(checks) >= limit:
                skip(source, start, end, "example_limit_reached")
                return
            digest = _V10Visible_hashlib.sha256(
                _V10Visible_json.dumps(
                    [source, start, end, quote], ensure_ascii=False, separators=(",", ":")
                ).encode("utf-8")
            ).hexdigest()[:24]
            indexed[identity] = len(checks)
            checks.append(
                {
                    "id": "visible_example_" + digest,
                    "kind": "exact",
                    "args": args,
                    "kwargs": kwargs,
                    "target": "return",
                    "expected": expected,
                    "evidence": [reference],
                    "derivation": _V10Visible_DERIVATION + "; surface=" + surface,
                }
            )

        for source, text in (("prompt", prompt), ("actual_answer", answer)):
            # Full Python sources/fences support multiline literal examples. Lines
            # and inline code spans support examples in otherwise non-Python prose.
            fragments = [(text, 0)]
            fragments += [
                (match.group(1), match.start(1))
                for match in _V10Visible_re.finditer(
                    r"(?ms)^\s*```(?:python|py)?[^\n]*\n(.*?)^\s*```", text
                )
            ]
            offset = 0
            for line in text.splitlines(keepends=True):
                stripped = line.strip()
                if stripped:
                    start = offset + len(line) - len(line.lstrip())
                    fragments.append((stripped, start))
                offset += len(line)
            fragments += [
                (match.group(1), match.start(1))
                for match in _V10Visible_re.finditer(r"(?<!`)`([^`\n]+)`(?!`)", text)
            ]
            fragment_keys = set()
            data_ranges = []
            for fragment, base in fragments:
                if (fragment, base) in fragment_keys:
                    continue
                fragment_keys.add((fragment, base))
                if any(start <= base < end for start, end in data_ranges):
                    continue
                try:
                    tree = _V10Visible_ast.parse(fragment)
                except (SyntaxError, ValueError, RecursionError):
                    tree = None
                if tree is not None:
                    data_ranges += [
                        (base + start, base + end)
                        for start, end in _V10Visible__data_ranges(fragment, tree)
                    ]
                    for statement in _V10Visible_ast.walk(tree):
                        expression = (
                            statement.test
                            if isinstance(statement, _V10Visible_ast.Assert)
                            else (
                                statement.value
                                if isinstance(statement, _V10Visible_ast.Expr)
                                else None
                            )
                        )
                        if not isinstance(expression, _V10Visible_ast.Compare):
                            continue
                        start, end = _V10Visible__node_span(fragment, statement)
                        try:
                            add(
                                _V10Visible__comparison(expression, entry_point),
                                source,
                                text,
                                base + start,
                                base + end,
                                "python_equality",
                            )
                        except (
                            LiteralExampleError,
                            ValueError,
                            TypeError,
                            RecursionError,
                        ) as error:
                            skip(source, base + start, base + end, str(error))
                    continue
                # Mapping syntax must occupy the complete bounded fragment. The
                # left side is parsed as one direct call, never a guessed call prefix.
                for match in _V10Visible_re.finditer(r"(?s)\)\s*(?:=>|->|→|=(?!=|>))\s*", fragment):
                    split = match.start() + 1
                    try:
                        call = _V10Visible_ast.parse(fragment[:split].strip(), mode="eval").body
                        expected = _V10Visible_ast.parse(
                            fragment[match.end() :].strip(), mode="eval"
                        ).body
                        args, kwargs = _V10Visible__call(call, entry_point)
                        add(
                            (args, kwargs, _V10Visible__typed(_V10Visible__literal(expected))),
                            source,
                            text,
                            base,
                            base + len(fragment),
                            "literal_mapping",
                        )
                        break
                    except (
                        SyntaxError,
                        LiteralExampleError,
                        ValueError,
                        TypeError,
                        RecursionError,
                    ) as error:
                        if entry_point in fragment:
                            skip(source, base, base + len(fragment), str(error))
            try:
                examples = _V10Visible_doctest.DocTestParser().get_examples(text)
            except ValueError:
                examples = []
            lines = text.splitlines(keepends=True)
            offsets = _V10Visible__offsets(text)
            for example in examples:
                start = offsets[example.lineno]
                if any(begin <= start < finish for begin, finish in data_ranges):
                    continue
                output_lines = example.want.splitlines(keepends=True)
                # A closing Python docstring delimiter is not expected output.
                for index, line in enumerate(output_lines):
                    if line.strip() in {'"""', "'''"}:
                        output_lines = output_lines[:index]
                        break
                wanted = "".join(output_lines).strip()
                end_line = min(
                    len(lines),
                    example.lineno + len(example.source.splitlines()) + len(output_lines),
                )
                end = offsets[end_line]
                try:
                    body = _V10Visible_ast.parse(example.source).body
                    if len(body) != 1 or not isinstance(body[0], _V10Visible_ast.Expr):
                        raise LiteralExampleError("doctest_direct_expression_required")
                    args, kwargs = _V10Visible__call(body[0].value, entry_point)
                    expected = _V10Visible__typed(
                        _V10Visible__literal(_V10Visible_ast.parse(wanted, mode="eval").body)
                    )
                    add((args, kwargs, expected), source, text, start, end, "doctest_literal_repr")
                except (
                    SyntaxError,
                    LiteralExampleError,
                    ValueError,
                    TypeError,
                    RecursionError,
                ) as error:
                    skip(source, start, end, str(error))
        return {"checks": _V10Visible_copy.deepcopy(checks), "skipped": skipped}

    # Frozen source: pilot/intentbridge_pass1_20261102/algorithm.py
    """Pass@1 coding ablations over the unchanged always-ask question policy.

Fresh programs share the same literal visible Q/A. Self-checks remain fallible:
all proposals require independent admission and real supplied-environment
execution; only strict pass-set improvement may replace the preserved program.
"""

    import copy as _V10Pass1_copy
    import hashlib as _V10Pass1_hashlib
    import json as _V10Pass1_json
    import keyword as _V10Pass1_keyword

    _V10Pass1_DEFAULT_POLICY = _V10Pass1_copy.deepcopy(_V10Question_DEFAULT_POLICY)
    _V10Pass1_BASELINE_CLASS = _V10Question_IntentBridgeQuestionLearningClarifier
    _V10Pass1_VARIANTS = ("baseline", "literal_examples", "proactive", "combined", "direct")
    _V10Pass1_PANEL_CHECK_LIMIT = _V10V2_MAX_CHECKS + 2

    _V10Pass1_INDEPENDENT_INSTRUCTIONS = (
        _V10V2_SOLVE_INSTRUCTIONS
        + """This is a fresh
post-answer synthesis from the complete visible task and literal actual Q/A.
No other candidate, previous observations, working brief or guessed solution is
provided. Implement the SAME stated requirements; do not sample a different
intent or invent missing facts. Return one complete fenced Python program.
"""
    )

    _V10Pass1_PANEL_INSTRUCTIONS = (
        _V10V2_GROUNDING
        + _V10V3_REFERENCE_INSTRUCTIONS
        + _V10Checks_CHECK_SEMANTICS_INSTRUCTIONS
        + _V10V2_TYPED_INSTRUCTIONS
        + _V10V3_CHECK_OBJECT_SCHEMA
        + """Propose at most TWO source-grounded checks
for a shared comparison panel without seeing any candidate code or execution
output. Exercise the stated main operation on a meaningful ordinary input and,
when justified, a boundary of its known legal domain. Do not invent an input
contract, exact type, expected value or property from convention or confidence.
Unknown or contradictory requirements remain unresolved, not fabricated tests.
Every check still needs separate independent admission and actual execution.
Use fresh IDs beginning pass1_panel_ and avoid reserved_check_ids. Return JSON
{checks:[CHECK],unresolved:[string]}; empty checks are allowed.
"""
    )

    class _V10Pass1__Run(_V10Question__Run):
        def __init__(self, config, policy, problem, *, variant, conditioned=False):
            super().initialize(config, policy, problem, conditioned=conditioned)
            if variant not in _V10Pass1_VARIANTS or variant == "baseline":
                raise ValueError("independent_pass1_variant_required")
            self.variant = variant
            self.literalEpoch = None
            self.artifacts["variant"] = "intentbridge_pass1_" + variant
            self.artifacts["pass1"] = {
                "ablation": variant,
                "literal_examples": [],
                "independent_syntheses": [],
                "shared_panel": None,
                "original_implementation_status": None,
                "self_checks_are_correctness_oracle": False,
            }
            self.artifacts["mechanisms"].update(
                literal_example_proposed=0,
                literal_example_admitted=0,
                independent_candidate_slots=0,
                independent_generation_requests=0,
                shared_panel_generation_calls=0,
                shared_panel_proposed=0,
                shared_panel_admitted=0,
                shared_panel_probe_runs=0,
                shared_panel_selection_updates=0,
            )

        def visible_qa(self):
            return {
                "task": _V10Pass1_copy.deepcopy(self.problem),
                "actual_question": self.qa[0],
                "actual_answer": self.qa[1],
                "qa_epoch": self.epoch,
                "qa_hash": self.digest,
            }

        def review(self, env, candidate, proposals, *, additions=False):
            if (
                self.variant in {"literal_examples", "combined"}
                and additions
                and self.literalEpoch != (self.epoch, self.digest)
            ):
                self.literalEpoch = (self.epoch, self.digest)
                extracted = _V10Visible_extract_visible_examples(self.problem, self.qa[1], limit=2)
                existing = {item["id"] for item in self.artifacts["checks"]["proposed"]}
                literal = self.checks_from(
                    {"checks": extracted["checks"]}, limit=2, existing_ids=existing
                )
                self.artifacts["pass1"]["literal_examples"].append(
                    {
                        "qa_hash": self.digest,
                        "qa_epoch": self.epoch,
                        "proposed_ids": [item["id"] for item in literal],
                        "skipped": _V10Pass1_copy.deepcopy(extracted["skipped"]),
                        "automatic_admission": False,
                    }
                )
                self.count("literal_example_proposed", len(literal))
                before = {item["id"] for item in self.artifacts["checks"]["admitted"]}
                result = super().review(env, candidate, literal + list(proposals), additions=True)
                admitted = {item["id"] for item in self.artifacts["checks"]["admitted"]} - before
                self.count(
                    "literal_example_admitted", sum(item["id"] in admitted for item in literal)
                )
                return result
            return super().review(env, candidate, proposals, additions=additions)

        def independent_generate(self, env, *, purpose):
            """Use a fresh candidate-local history, never another program/brief."""
            slot = len(self.artifacts["candidates"])
            if slot >= self.config["max_candidates"]:
                return None
            item = {
                "candidate_id": "candidate_" + str(slot),
                "qa_epoch": self.epoch,
                "qa_hash": self.digest,
                "trigger": {"kind": purpose},
                "code": "",
                "eligible": False,
                "format_errors": [],
                "observations": None,
                "independent_synthesis": True,
            }
            self.artifacts["candidates"].append(item)
            self.count("candidate_slots")
            self.count("independent_candidate_slots")
            payload = self.visible_qa()
            messages = [
                {
                    "role": "user",
                    "content": _V10Pass1_INDEPENDENT_INSTRUCTIONS
                    + self.guidance("solve_guidance")
                    + _V10Pass1_json.dumps(payload, ensure_ascii=False),
                }
            ]
            self.artifacts["pass1"]["independent_syntheses"].append(
                {
                    "candidate_id": item["candidate_id"],
                    "purpose": purpose,
                    "qa_hash": self.digest,
                    "qa_epoch": self.epoch,
                    "other_candidate_or_brief_supplied": False,
                }
            )
            for attempt in range(self.config["repair_attempts"] + 1):
                self.count("generation_requests")
                self.count("independent_generation_requests")
                # Transport/configuration errors escape, including ValueError.
                raw = env.llm(messages)
                try:
                    code = _V10V2_parse_candidate(raw, self.problem)
                except (SyntaxError, TypeError, ValueError, AttributeError) as error:
                    event = {"attempt": attempt, "error": _IBTypeName(error), "detail": str(error)}
                    item["format_errors"].append(event)
                    self.count("code_format_rejections")
                    self.record(
                        phase="independent_synthesis",
                        status="format_error",
                        candidate_id=item["candidate_id"],
                        **event,
                    )
                    if attempt < self.config["repair_attempts"]:
                        self.count("format_repairs")
                        messages.extend(
                            [
                                {
                                    "role": "assistant",
                                    "content": raw if isinstance(raw, str) else "",
                                },
                                {
                                    "role": "user",
                                    "content": "Repair only this program's structural error: "
                                    + str(error)
                                    + ". Preserve the complete task and literal Q/A. Return a complete Python fence implementing "
                                    + self.problem["entry_point"]
                                    + ". Do not ask another human.",
                                },
                            ]
                        )
                    continue
                item.update(
                    code=code,
                    eligible=True,
                    code_sha256=_V10Pass1_hashlib.sha256(code.encode("utf-8")).hexdigest(),
                )
                self.count("valid_candidates")
                # This slot is deliberately NOT counted as repair_generated.
                return item
            item["rejection_reason"] = "independent_structural_format_exhausted"
            return None

        def shared_panel(self, env, preserved):
            current = [
                item
                for item in self.artifacts["candidates"]
                if item["eligible"]
                and item["qa_hash"] == self.digest
                and item["qa_epoch"] == self.epoch
            ]
            if not current:
                self.artifacts["status"] = "proactive_no_valid_current_qa_candidate"
                return
            if preserved is None:
                preserved = current[0]
                preserved["selection_reason"] = "first_valid_current_qa_independent_synthesis"
            self.best = preserved
            admitted = self.artifacts["checks"]["admitted"]
            remaining = min(2, max(0, _V10Pass1_PANEL_CHECK_LIMIT - len(admitted)))
            panel = {
                "qa_hash": self.digest,
                "qa_epoch": self.epoch,
                "preserved_candidate_id": preserved["candidate_id"],
                "candidate_ids": [c["candidate_id"] for c in current],
                "candidate_code_or_observations_supplied_to_check_generation": False,
                "admitted_ids": [],
                "observation_unknown_candidate_ids": [],
                "selection_updates": [],
                "panel_limit": _V10Pass1_PANEL_CHECK_LIMIT,
            }
            self.artifacts["pass1"]["shared_panel"] = panel
            if remaining:
                existing = {item["id"] for item in self.artifacts["checks"]["proposed"]}
                existing.update(item["id"] for item in admitted)
                payload = {
                    **self.visible_qa(),
                    "reserved_check_ids": sorted(existing),
                    "evidence_catalog": self.catalog(),
                }

                def schema(value):
                    if (
                        not isinstance(value, dict)
                        or set(value) != {"checks", "unresolved"}
                        or not isinstance(value["checks"], list)
                        or not isinstance(value["unresolved"], list)
                        or not all(isinstance(x, str) for x in value["unresolved"])
                    ):
                        raise ValueError("shared_panel_schema_invalid")
                    return value

                self.count("shared_panel_generation_calls")
                raw = self.json_call(
                    env, _V10Pass1_PANEL_INSTRUCTIONS, payload, "shared_panel_generation", schema
                )
                proposals = self.checks_from(raw, limit=remaining, existing_ids=existing)
                self.count("shared_panel_proposed", len(proposals))
                assessment = self.blind_assess(env, proposals)
                before = {item["id"] for item in admitted}
                self.admit(proposals, assessment["accepted_ids"])
                panel["admitted_ids"] = [
                    item["id"] for item in admitted if item["id"] not in before
                ]
                self.count("shared_panel_admitted", len(panel["admitted_ids"]))
            if len(admitted) > _V10Pass1_PANEL_CHECK_LIMIT:
                raise RuntimeError("shared_panel_limit_exceeded")
            # Bypass inherited coverage hooks: every candidate sees one identical,
            # completely frozen panel before any new selection is attempted.
            for item in current:
                self.count("shared_panel_probe_runs")
                rows = _V10V3__Run.execute_checks(self, env, item)
                if rows is None:
                    panel["observation_unknown_candidate_ids"].append(item["candidate_id"])
            if preserved.get("observations") is None:
                self.best = preserved
                self.artifacts["status"] = "proactive_observation_unknown_preserve_candidate"
                return
            for item in current:
                if item.get("observations") is None:
                    continue
                if self.passed(self.best, admitted) < self.passed(item, admitted):
                    before = self.best["candidate_id"]
                    self.best = item
                    item["selection_reason"] = "shared_panel_strict_improvement_without_regression"
                    panel["selection_updates"].append(
                        {"before": before, "after": item["candidate_id"]}
                    )
                    self.count("shared_panel_selection_updates")
            self.artifacts["status"] = "proactive_shared_panel_visible_best"

        def implement(self, env):
            if self.variant == "direct":
                # The direct control intentionally has no brief, review or probes.
                item = self.independent_generate(env, purpose="direct_post_answer_synthesis")
                if item is not None:
                    self.best = item
                    item["selection_reason"] = "first_valid_direct_current_qa_program"
                    self.artifacts["status"] = "direct_current_qa_program_no_internal_checks"
                else:
                    self.artifacts["status"] = "direct_no_valid_current_qa_program"
                return
            super().implement(env)
            self.artifacts["pass1"]["original_implementation_status"] = self.artifacts["status"]
            if self.variant not in {"proactive", "combined"}:
                return
            preserved = self.best
            while len(self.artifacts["candidates"]) < self.config["max_candidates"]:
                self.independent_generate(env, purpose="independent_post_answer_synthesis")
            self.shared_panel(env, preserved)

        initialize = __init__

    class _V10Pass1_IntentBridgePass1Clarifier(_V10Question_IntentBridgeQuestionLearningClarifier):
        """Fixed-policy coding mechanisms with unchanged single-question behavior."""

        DEFAULT_CONFIG = dict(_V10Question_IntentBridgeQuestionLearningClarifier.DEFAULT_CONFIG)

        def __init__(self, config=None, *, variant="proactive", policy=None):
            if variant not in _V10Pass1_VARIANTS or variant == "baseline":
                raise ValueError("use_exact_baseline_class_for_baseline_arm")
            if policy is not None and policy != _V10Pass1_DEFAULT_POLICY:
                raise ValueError("pass1_ablation_policy_is_fixed")
            self.variant = variant
            super().initialize(config=config, policy=_V10Pass1_DEFAULT_POLICY)

        def localRun(self, env, problem, fixed_qa=None):
            for field, ceiling in self.DEFAULT_CONFIG.items():
                if type(self.config[field]) is not int or not 0 <= self.config[field] <= ceiling:
                    raise ValueError(field + " must be an integer within the fixed default ceiling")
            if self.config["max_candidates"] < 1 or self.policy != _V10Pass1_DEFAULT_POLICY:
                raise ValueError("fixed_policy_and_positive_candidate_capacity_required")
            visible = {"prompt": problem["prompt"], "entry_point": problem["entry_point"]}
            if (
                not isinstance(visible["prompt"], str)
                or not isinstance(visible["entry_point"], str)
                or not visible["entry_point"].isidentifier()
                or _V10Pass1_keyword.iskeyword(visible["entry_point"])
            ):
                raise ValueError("invalid_visible_task_or_entry_point")
            state = _V10Pass1__Run(
                dict(self.config),
                _V10Pass1_copy.deepcopy(self.policy),
                visible,
                variant=self.variant,
                conditioned=fixed_qa is not None,
            )
            try:
                return state.execute(env, fixed_qa)
            finally:
                self.artifacts, self.trace = (
                    _V10Pass1_copy.deepcopy(state.artifacts),
                    _V10Pass1_copy.deepcopy(state.trace),
                )

        initialize = __init__

    def _V10Pass1_make_algorithm(variant, *, config=None, policy=None):
        """The baseline is the exact delivered class, without an ablation wrapper."""
        if policy is not None and policy != _V10Pass1_DEFAULT_POLICY:
            raise ValueError("pass1_ablation_policy_is_fixed")
        if variant == "baseline":
            return _V10Pass1_BASELINE_CLASS(config=config, policy=_V10Pass1_DEFAULT_POLICY)
        return _V10Pass1_IntentBridgePass1Clarifier(config=config, variant=variant, policy=policy)

    # Frozen source: pilot/intentbridge_component_ablation_20261102/algorithm.py
    """Independent component removals over the frozen mandatory-question baseline.

These experimental controls preserve visible-source projection, typed execution,
Q/A binding and the single real-question protocol. They are not evidence of
effectiveness. No existing algorithm or paid trajectory is modified.
"""

    import copy as _V10Component_copy
    import keyword as _V10Component_keyword

    _V10Component_DEFAULT_POLICY = _V10Component_copy.deepcopy(_V10Question_DEFAULT_POLICY)
    _V10Component_BASELINE_CLASS = _V10Question_IntentBridgeQuestionLearningClarifier
    _V10Component_CODING_ARMS = (
        "baseline",
        "no_brief",
        "exact_only",
        "no_code_review",
        "no_main_coverage",
        "no_review_completion",
        "no_semantic_repair",
        "no_blind_admission",
        "candidates_only",
        "shared_checks_only",
        "first_program_only",
    )
    _V10Component_QUESTION_ARMS = ("baseline", "question_no_profile")
    _V10Component_VARIANTS = _V10Component_CODING_ARMS + ("question_no_profile",)

    class _V10Component__Run(_V10Question__Run):
        def __init__(self, config, policy, problem, *, variant, conditioned=False):
            if variant not in _V10Component_VARIANTS or variant == "baseline":
                raise ValueError("component_ablation_requires_nonbaseline_arm")
            config = dict(config)
            if variant == "no_semantic_repair":
                config["semantic_rounds"] = 0
            super().initialize(config, policy, problem, conditioned=conditioned)
            self.variant = variant
            self.artifacts["variant"] = "intentbridge_component_" + variant
            self.artifacts["component_ablation"] = {
                "arm": variant,
                "disabled_stages": [],
                "excluded_property_ids": [],
                "candidate_comparison": None,
                "question_profile_omitted": False,
                "self_checks_are_correctness_oracle": False,
            }
            # The two split-A arms reuse the frozen independent synthesis and panel
            # methods without changing their prompts or their observation semantics.
            self.artifacts["pass1"] = {
                "ablation": variant,
                "literal_examples": [],
                "independent_syntheses": [],
                "shared_panel": None,
                "original_implementation_status": None,
                "self_checks_are_correctness_oracle": False,
            }
            self.artifacts["mechanisms"].update(
                component_brief_omitted=0,
                component_properties_excluded=0,
                component_code_review_omitted=0,
                component_main_coverage_omitted=0,
                component_review_completion_omitted=0,
                component_blind_admission_omitted=0,
                component_first_program_restored=0,
                independent_candidate_slots=0,
                independent_generation_requests=0,
                shared_panel_generation_calls=0,
                shared_panel_proposed=0,
                shared_panel_admitted=0,
                shared_panel_probe_runs=0,
                shared_panel_selection_updates=0,
            )
            if variant == "no_semantic_repair":
                self.omit("semantic_repair")

        def omit(self, stage):
            stages = self.artifacts["component_ablation"]["disabled_stages"]
            if stage not in stages:
                stages.append(stage)

        def brief(self, env):
            if self.variant != "no_brief":
                return super().brief(env)
            self.omit("implementation_brief")
            self.count("component_brief_omitted")
            self.artifacts["implementation_brief"] = {
                "confirmed": [],
                "scope_updates": [],
                "unresolved": [],
                "fallback": True,
                "ablation_omitted": True,
                "qa_epoch": self.epoch,
                "qa_hash": self.digest,
            }

        def checks_from(self, value, *, limit, existing_ids=()):
            if self.variant != "exact_only":
                return super().checks_from(value, limit=limit, existing_ids=existing_ids)
            self.omit("property_checks")
            # Apply the same limit to the same proposed list before removing
            # properties; do not silently backfill with more exact checks.
            proposals = super().checks_from(value, limit=limit, existing_ids=existing_ids)
            excluded = [item["id"] for item in proposals if item["kind"] == "property"]
            self.artifacts["component_ablation"]["excluded_property_ids"].extend(excluded)
            self.count("component_properties_excluded", len(excluded))
            self.artifacts["checks"]["rejected"].extend(
                {"id": ident, "reason": "property_excluded_by_exact_only_ablation"}
                for ident in excluded
            )
            self.count("check_rejected", len(excluded))
            return [item for item in proposals if item["kind"] == "exact"]

        def blind_assess(self, env, proposals, *, diagnosis=None):
            if self.variant != "no_blind_admission":
                return super().blind_assess(env, proposals, diagnosis=diagnosis)
            if not proposals:
                return {"accepted_ids": [], "rejected": [], "conclusive_rejected_ids": []}
            self.omit("semantic_blind_check_admission")
            self.count("component_blind_admission_omitted")
            # This arm removes semantic LLM adjudication, never local type/schema or
            # literal-source validation. It cannot revoke checks on an unconfirmed
            # diagnosis: no semantic adjudication means no conclusive contradiction.
            canonical = self.canonical({"checks": proposals}, phase="ablation_local_admission")
            valid, rejected = _V10Checks_validate_checks(
                canonical,
                self.problem,
                self.qa[1],
                limit=_V10Pass1_PANEL_CHECK_LIMIT,
                existing_ids=(),
            )
            accepted = [item["id"] for item in valid]
            self.artifacts["blind_admissions"].append(
                {
                    "qa_hash": self.digest,
                    "qa_epoch": self.epoch,
                    "check_ids": [item.get("id", "") for item in proposals],
                    "accepted_ids": accepted,
                    "rejected": _V10Component_copy.deepcopy(rejected),
                    "challenge": diagnosis is not None,
                    "conclusive_rejected_ids": [],
                    "candidate_code_or_observations_supplied": False,
                    "semantic_adjudication_omitted": True,
                    "acceptance_means_semantic_support": False,
                }
            )
            return {"accepted_ids": accepted, "rejected": rejected, "conclusive_rejected_ids": []}

        def review(self, env, candidate, proposals, *, additions=False):
            if self.variant != "no_code_review":
                return super().review(env, candidate, proposals, additions=additions)
            self.omit("candidate_code_review")
            self.count("component_code_review_omitted")
            if additions and proposals:
                assessment = self.blind_assess(env, proposals)
                self.admit(proposals, assessment["accepted_ids"])
            clean = {
                "candidate_id": candidate["candidate_id"],
                "qa_hash": self.digest,
                "issues": [],
                "check_objections": [],
                "unresolved": [],
                "reason": "Candidate review omitted by component ablation.",
                "ablation_omitted": True,
            }
            self.artifacts["reviews"].append(_V10Component_copy.deepcopy(clean))
            self.candidateReviews[(self.digest, candidate["candidate_id"])] = clean
            # Preserve the normal hook and the candidate-blind v5 coverage stage;
            # an omitted code reviewer is not permission to omit every check audit.
            if candidate is self.best and candidate.get("observations") is not None:
                self.complete_check_coverage(env, candidate, clean)
                if self.best is not candidate:
                    return {**clean, "candidate_id": self.best["candidate_id"]}
            return clean

        def complete_check_coverage(self, env, candidate, reviewed):
            if self.variant == "no_main_coverage":
                if not reviewed.get("issues"):
                    self.omit("main_rule_coverage")
                    self.count("component_main_coverage_omitted")
                return _V10V4__Run.complete_check_coverage(self, env, candidate, reviewed)
            if self.variant == "no_review_completion" and reviewed.get("issues"):
                self.omit("review_issue_check_completion")
                self.count("component_review_completion_omitted")
                return
            return super().complete_check_coverage(env, candidate, reviewed)

        def visible_qa(self):
            return {
                "task": _V10Component_copy.deepcopy(self.problem),
                "actual_question": self.qa[0],
                "actual_answer": self.qa[1],
                "qa_epoch": self.epoch,
                "qa_hash": self.digest,
            }

        def independent_generate(self, env, *, purpose):
            return _V10Pass1__Run.independent_generate(self, env, purpose=purpose)

        def shared_panel(self, env, preserved):
            return _V10Pass1__Run.shared_panel(self, env, preserved)

        def existing_panel(self, env, preserved):
            """Compare independent implementations on identical existing checks."""
            current = [
                item
                for item in self.artifacts["candidates"]
                if item["eligible"]
                and item["qa_hash"] == self.digest
                and item["qa_epoch"] == self.epoch
            ]
            if not current:
                self.artifacts["status"] = "candidate_split_no_valid_current_qa_program"
                return
            if preserved is None:
                preserved = current[0]
                preserved["selection_reason"] = "first_valid_current_qa_independent_synthesis"
            self.best = preserved
            admitted = self.artifacts["checks"]["admitted"]
            panel = {
                "qa_hash": self.digest,
                "qa_epoch": self.epoch,
                "preserved_candidate_id": preserved["candidate_id"],
                "candidate_ids": [item["candidate_id"] for item in current],
                "admitted_check_ids": [item["id"] for item in admitted],
                "new_check_generation_calls": 0,
                "selection_updates": [],
                "observation_unknown_candidate_ids": [],
            }
            self.artifacts["component_ablation"]["candidate_comparison"] = panel
            # Bypass completion hooks so no arm-specific extra checks can enter after
            # the panel is frozen. Every current-Q/A candidate sees the same checks.
            for item in current:
                rows = _V10V3__Run.execute_checks(self, env, item)
                if rows is None:
                    panel["observation_unknown_candidate_ids"].append(item["candidate_id"])
            if preserved.get("observations") is None:
                self.artifacts["status"] = "candidate_split_unknown_observation_preserve"
                return
            for item in current:
                if item.get("observations") is not None and self.passed(
                    self.best, admitted
                ) < self.passed(item, admitted):
                    before = self.best["candidate_id"]
                    self.best = item
                    item["selection_reason"] = (
                        "existing_checks_strict_improvement_without_regression"
                    )
                    panel["selection_updates"].append(
                        {"before": before, "after": item["candidate_id"]}
                    )
            self.artifacts["status"] = "candidate_split_existing_panel_visible_best"

        def implement(self, env):
            super().implement(env)
            self.artifacts["pass1"]["original_implementation_status"] = self.artifacts["status"]
            if self.variant == "candidates_only":
                preserved = self.best
                while len(self.artifacts["candidates"]) < self.config["max_candidates"]:
                    self.independent_generate(env, purpose="independent_post_answer_synthesis")
                self.existing_panel(env, preserved)
            elif self.variant == "shared_checks_only":
                self.shared_panel(env, self.best)
            elif self.variant == "first_program_only":
                self.omit("final_candidate_reselection")
                eligible = [
                    item
                    for item in self.artifacts["candidates"]
                    if item["eligible"]
                    and item["qa_hash"] == self.digest
                    and item["qa_epoch"] == self.epoch
                ]
                if eligible:
                    chosen = eligible[0]
                    before = self.best["candidate_id"] if self.best else None
                    self.best = chosen
                    chosen["selection_reason"] = "first_valid_current_qa_program_control"
                    changed = before != chosen["candidate_id"]
                    self.count("component_first_program_restored", int(changed))
                    self.artifacts["component_ablation"]["candidate_comparison"] = {
                        "before": before,
                        "after": chosen["candidate_id"],
                        "computation_retained": True,
                        "selection_changed": changed,
                    }

        def plan_and_ask(self, env):
            if self.variant != "question_no_profile":
                return super().plan_and_ask(env)
            protocol = self.artifacts["question_protocol"]
            if self.asked or protocol["actual_invocations"]:
                self.incomplete("duplicate_question_attempt_forbidden")
            if not env.can_ask():
                self.incomplete("environment_cannot_ask")
            self.omit("main_decision_discovery")
            self.artifacts["component_ablation"]["question_profile_omitted"] = True
            profile = _V10Decisions_normalize_decision_profile(
                {"known_requirements": [], "main_unknowns": [], "other_unknowns": []}, self.problem
            )
            self.artifacts["decision_profile"] = _V10Component_copy.deepcopy(profile)
            self.artifacts["proposal"] = _V10Component_copy.deepcopy(profile)

            def schema(value):
                if (
                    not isinstance(value, dict)
                    or value.get("mode") not in {"uncertainty", "confirmation"}
                    or any(
                        not isinstance(value.get(field), str) or not value[field].strip()
                        for field in ("question", "target", "reason")
                    )
                ):
                    raise ValueError(
                        "mandatory_question_requires_nonempty_question_target_reason_and_valid_mode"
                    )
                return value

            meta = self.json_call(
                env,
                _V10Question_QUESTION_INSTRUCTIONS + self.guidance("plan_guidance"),
                _V10Decisions_build_question_payload(self.problem, profile),
                "question_selection",
                schema,
            )
            self.artifacts["question_meta"] = _V10Component_copy.deepcopy(meta or {})
            if meta is None:
                self.incomplete("question_format_recovery_exhausted")
            if not env.can_ask():
                self.incomplete("environment_cannot_ask_after_question_selection")
            question = meta["question"]
            self.count("question_attempted")
            self.set_qa(question, "", status="attempted")
            protocol.update(actual_invocations=1, status="attempted")
            try:
                answer = env.ask_human(question)
            except _V10V2_TooManyQuestionException as error:
                self.artifacts["qa_events"][-1]["status"] = "environment_refused"
                self.artifacts["question_protocol"]["status"] = "environment_refused"
                self.artifacts["status"] = "question_protocol_incomplete"
                raise QuestionProtocolIncomplete("environment_refused") from error
            if not isinstance(answer, str):
                self.artifacts["qa_events"][-1]["status"] = "invalid_answer_type"
                self.incomplete("actual_answer_must_be_string")
            self.qa = (question, answer)
            self.digest = _V10V2_qa_hash(self.problem, question, answer)
            self.artifacts["qa_events"][-1].update(
                answer=answer, status="completed", qa_hash=self.digest
            )
            protocol.update(completed_interactions=1, status="completed")

        initialize = __init__

    class _V10Component_IntentBridgeComponentClarifier(
        _V10Question_IntentBridgeQuestionLearningClarifier
    ):
        """One changed component per arm; safety and information boundaries remain."""

        DEFAULT_CONFIG = dict(_V10Question_IntentBridgeQuestionLearningClarifier.DEFAULT_CONFIG)

        def __init__(self, config=None, *, variant="no_brief", policy=None):
            if variant not in _V10Component_VARIANTS or variant == "baseline":
                raise ValueError("use_exact_baseline_class_for_baseline_arm")
            if policy is not None and policy != _V10Component_DEFAULT_POLICY:
                raise ValueError("component_ablation_policy_is_fixed")
            self.variant = variant
            if variant == "no_semantic_repair":
                config = dict(config or {})
                config["semantic_rounds"] = 0
            super().initialize(config=config, policy=_V10Component_DEFAULT_POLICY)

        def localRun(self, env, problem, fixed_qa=None):
            for field, ceiling in self.DEFAULT_CONFIG.items():
                if type(self.config[field]) is not int or not 0 <= self.config[field] <= ceiling:
                    raise ValueError(field + " must be an integer within the fixed default ceiling")
            if self.config["max_candidates"] < 1 or self.policy != _V10Component_DEFAULT_POLICY:
                raise ValueError("fixed_policy_and_positive_candidate_capacity_required")
            visible = {"prompt": problem["prompt"], "entry_point": problem["entry_point"]}
            if (
                not isinstance(visible["prompt"], str)
                or not isinstance(visible["entry_point"], str)
                or not visible["entry_point"].isidentifier()
                or _V10Component_keyword.iskeyword(visible["entry_point"])
            ):
                raise ValueError("invalid_visible_task_or_entry_point")
            state = _V10Component__Run(
                dict(self.config),
                _V10Component_copy.deepcopy(self.policy),
                visible,
                variant=self.variant,
                conditioned=fixed_qa is not None,
            )
            try:
                return state.execute(env, fixed_qa)
            finally:
                self.artifacts, self.trace = (
                    _V10Component_copy.deepcopy(state.artifacts),
                    _V10Component_copy.deepcopy(state.trace),
                )

        initialize = __init__

    def _V10Component_make_algorithm(variant, *, config=None, policy=None):
        if variant not in _V10Component_VARIANTS:
            raise ValueError("unknown_component_ablation_arm")
        if policy is not None and policy != _V10Component_DEFAULT_POLICY:
            raise ValueError("component_ablation_policy_is_fixed")
        if variant == "baseline":
            return _V10Component_BASELINE_CLASS(config=config, policy=_V10Component_DEFAULT_POLICY)
        return _V10Component_IntentBridgeComponentClarifier(
            config=config, variant=variant, policy=policy
        )

    class IntentBridgeComponentClarifier(_V10Component_IntentBridgeComponentClarifier):
        """Exact frozen question_no_profile variant; historical local candidate."""

        def __init__(self, config=None):
            super().initialize(
                config=config, variant="question_no_profile", policy=_V10Component_DEFAULT_POLICY
            )

    _IBOriginalTypeNames = {
        _V10Original__TaskRun: "_TaskRun",
        _V10Original_IntentBridgeClarifier: "IntentBridgeClarifier",
        _V10V2__Run: "_Run",
        _V10V2_IntentBridgeV2Clarifier: "IntentBridgeV2Clarifier",
        EvidenceValidationError: "EvidenceValidationError",
        _V10V3__Run: "_Run",
        _V10V3_IntentBridgeV3Clarifier: "IntentBridgeV3Clarifier",
        _CompletionObservationUnknown: "_CompletionObservationUnknown",
        _V10V4__Run: "_Run",
        _V10V4_IntentBridgeV4Clarifier: "IntentBridgeV4Clarifier",
        _V10V5__Run: "_Run",
        _V10V5_IntentBridgeV5Clarifier: "IntentBridgeV5Clarifier",
        QuestionProtocolIncomplete: "QuestionProtocolIncomplete",
        _V10Question__Run: "_Run",
        _V10Question_IntentBridgeQuestionLearningClarifier: "IntentBridgeQuestionLearningClarifier",
        LiteralExampleError: "LiteralExampleError",
        _V10Pass1__Run: "_Run",
        _V10Pass1_IntentBridgePass1Clarifier: "IntentBridgePass1Clarifier",
        _V10Component__Run: "_Run",
        _V10Component_IntentBridgeComponentClarifier: "IntentBridgeComponentClarifier",
        IntentBridgeComponentClarifier: "IntentBridgeComponentClarifier",
    }

    return {
        "EvidenceValidationError": EvidenceValidationError,
        "LiteralExampleError": LiteralExampleError,
        "QuestionProtocolIncomplete": QuestionProtocolIncomplete,
        "_CompletionObservationUnknown": _CompletionObservationUnknown,
        "_V10Checks_CHECK_SCHEMA": _V10Checks_CHECK_SCHEMA,
        "_V10Checks_CHECK_SEMANTICS_INSTRUCTIONS": _V10Checks_CHECK_SEMANTICS_INSTRUCTIONS,
        "_V10Checks__literal_data_ranges": _V10Checks__literal_data_ranges,
        "_V10Checks__reference": _V10Checks__reference,
        "_V10Checks__typed_equal": _V10Checks__typed_equal,
        "_V10Checks__visible_calls": _V10Checks__visible_calls,
        "_V10Checks__visible_signatures": _V10Checks__visible_signatures,
        "_V10Checks__within_literal": _V10Checks__within_literal,
        "_V10Checks_ast": _V10Checks_ast,
        "_V10Checks_copy": _V10Checks_copy,
        "_V10Checks_extension_property_satisfied": _V10Checks_extension_property_satisfied,
        "_V10Checks_invocation_provenance": _V10Checks_invocation_provenance,
        "_V10Checks_io": _V10Checks_io,
        "_V10Checks_probe_script": _V10Checks_probe_script,
        "_V10Checks_re": _V10Checks_re,
        "_V10Checks_tokenize": _V10Checks_tokenize,
        "_V10Checks_validate_checks": _V10Checks_validate_checks,
        "_V10Component_BASELINE_CLASS": _V10Component_BASELINE_CLASS,
        "_V10Component_CODING_ARMS": _V10Component_CODING_ARMS,
        "_V10Component_DEFAULT_POLICY": _V10Component_DEFAULT_POLICY,
        "_V10Component_IntentBridgeComponentClarifier": _V10Component_IntentBridgeComponentClarifier,
        "_V10Component_QUESTION_ARMS": _V10Component_QUESTION_ARMS,
        "_V10Component_VARIANTS": _V10Component_VARIANTS,
        "_V10Component__Run": _V10Component__Run,
        "_V10Component_copy": _V10Component_copy,
        "_V10Component_keyword": _V10Component_keyword,
        "_V10Component_make_algorithm": _V10Component_make_algorithm,
        "_V10Coverage_MAX_COMPLETION_CHECKS": _V10Coverage_MAX_COMPLETION_CHECKS,
        "_V10Coverage_MAX_OBLIGATIONS": _V10Coverage_MAX_OBLIGATIONS,
        "_V10Coverage__REPORT_FIELDS": _V10Coverage__REPORT_FIELDS,
        "_V10Coverage__SHARED_CHECK_FIELDS": _V10Coverage__SHARED_CHECK_FIELDS,
        "_V10Coverage__check_projection": _V10Coverage__check_projection,
        "_V10Coverage__json": _V10Coverage__json,
        "_V10Coverage__sha": _V10Coverage__sha,
        "_V10Coverage__strings": _V10Coverage__strings,
        "_V10Coverage_build_coverage_payload": _V10Coverage_build_coverage_payload,
        "_V10Coverage_copy": _V10Coverage_copy,
        "_V10Coverage_hashlib": _V10Coverage_hashlib,
        "_V10Coverage_json": _V10Coverage_json,
        "_V10Coverage_validate_coverage_report": _V10Coverage_validate_coverage_report,
        "_V10Decisions_PROFILE_FIELDS": _V10Decisions_PROFILE_FIELDS,
        "_V10Decisions__DECISION_FIELDS": _V10Decisions__DECISION_FIELDS,
        "_V10Decisions__FACT_FIELDS": _V10Decisions__FACT_FIELDS,
        "_V10Decisions__error": _V10Decisions__error,
        "_V10Decisions__prompt_evidence": _V10Decisions__prompt_evidence,
        "_V10Decisions__visible_task": _V10Decisions__visible_task,
        "_V10Decisions_build_question_payload": _V10Decisions_build_question_payload,
        "_V10Decisions_normalize_decision_profile": _V10Decisions_normalize_decision_profile,
        "_V10Evidence_BRIEF_FIELDS": _V10Evidence_BRIEF_FIELDS,
        "_V10Evidence_CATALOG_VERSION": _V10Evidence_CATALOG_VERSION,
        "_V10Evidence_SOURCES": _V10Evidence_SOURCES,
        "_V10Evidence_SPAN_CHARS": _V10Evidence_SPAN_CHARS,
        "_V10Evidence__authority": _V10Evidence__authority,
        "_V10Evidence__checked_catalog": _V10Evidence__checked_catalog,
        "_V10Evidence__context_hash": _V10Evidence__context_hash,
        "_V10Evidence__error": _V10Evidence__error,
        "_V10Evidence__same_json": _V10Evidence__same_json,
        "_V10Evidence__sha": _V10Evidence__sha,
        "_V10Evidence_build_evidence_catalog": _V10Evidence_build_evidence_catalog,
        "_V10Evidence_copy": _V10Evidence_copy,
        "_V10Evidence_hashlib": _V10Evidence_hashlib,
        "_V10Evidence_json": _V10Evidence_json,
        "_V10Evidence_merge_brief_repair": _V10Evidence_merge_brief_repair,
        "_V10Evidence_re": _V10Evidence_re,
        "_V10Evidence_resolve_evidence": _V10Evidence_resolve_evidence,
        "_V10Evidence_validate_brief_partial": _V10Evidence_validate_brief_partial,
        "_V10Evidence_validate_evidence": _V10Evidence_validate_evidence,
        "_V10Original_ClarificationAlgorithmBase": _V10Original_ClarificationAlgorithmBase,
        "_V10Original_IntentBridgeClarifier": _V10Original_IntentBridgeClarifier,
        "_V10Original_LimitsExceededException": _V10Original_LimitsExceededException,
        "_V10Original_TooManyQuestionException": _V10Original_TooManyQuestionException,
        "_V10Original__TaskRun": _V10Original__TaskRun,
        "_V10Original_ast": _V10Original_ast,
        "_V10Original_json": _V10Original_json,
        "_V10Original_json_object": _V10Original_json_object,
        "_V10Original_python_code": _V10Original_python_code,
        "_V10Original_re": _V10Original_re,
        "_V10Pass1_BASELINE_CLASS": _V10Pass1_BASELINE_CLASS,
        "_V10Pass1_DEFAULT_POLICY": _V10Pass1_DEFAULT_POLICY,
        "_V10Pass1_INDEPENDENT_INSTRUCTIONS": _V10Pass1_INDEPENDENT_INSTRUCTIONS,
        "_V10Pass1_IntentBridgePass1Clarifier": _V10Pass1_IntentBridgePass1Clarifier,
        "_V10Pass1_PANEL_CHECK_LIMIT": _V10Pass1_PANEL_CHECK_LIMIT,
        "_V10Pass1_PANEL_INSTRUCTIONS": _V10Pass1_PANEL_INSTRUCTIONS,
        "_V10Pass1_VARIANTS": _V10Pass1_VARIANTS,
        "_V10Pass1__Run": _V10Pass1__Run,
        "_V10Pass1_copy": _V10Pass1_copy,
        "_V10Pass1_hashlib": _V10Pass1_hashlib,
        "_V10Pass1_json": _V10Pass1_json,
        "_V10Pass1_keyword": _V10Pass1_keyword,
        "_V10Pass1_make_algorithm": _V10Pass1_make_algorithm,
        "_V10Protocol__assessment_errors": _V10Protocol__assessment_errors,
        "_V10Protocol__binding": _V10Protocol__binding,
        "_V10Protocol__checked_previous": _V10Protocol__checked_previous,
        "_V10Protocol__error": _V10Protocol__error,
        "_V10Protocol__facet_errors": _V10Protocol__facet_errors,
        "_V10Protocol__json": _V10Protocol__json,
        "_V10Protocol__merge_record_fields": _V10Protocol__merge_record_fields,
        "_V10Protocol__proposal_ids": _V10Protocol__proposal_ids,
        "_V10Protocol_citation_repair_targets": _V10Protocol_citation_repair_targets,
        "_V10Protocol_copy": _V10Protocol_copy,
        "_V10Protocol_hashlib": _V10Protocol_hashlib,
        "_V10Protocol_json": _V10Protocol_json,
        "_V10Protocol_merge_facet_citation_repairs": _V10Protocol_merge_facet_citation_repairs,
        "_V10Protocol_merge_facet_repair": _V10Protocol_merge_facet_repair,
        "_V10Protocol_parse_facet_response": _V10Protocol_parse_facet_response,
        "_V10Protocol_validate_checks": _V10Protocol_validate_checks,
        "_V10Question_DEFAULT_POLICY": _V10Question_DEFAULT_POLICY,
        "_V10Question_IntentBridgeQuestionLearningClarifier": _V10Question_IntentBridgeQuestionLearningClarifier,
        "_V10Question_QUESTION_INSTRUCTIONS": _V10Question_QUESTION_INSTRUCTIONS,
        "_V10Question__Run": _V10Question__Run,
        "_V10Question_copy": _V10Question_copy,
        "_V10Question_keyword": _V10Question_keyword,
        "_V10Review_BLIND_DERIVATION": _V10Review_BLIND_DERIVATION,
        "_V10Review_DIAGNOSIS_INSTRUCTIONS": _V10Review_DIAGNOSIS_INSTRUCTIONS,
        "_V10Review_FACETS": _V10Review_FACETS,
        "_V10Review_FACET_INSTRUCTIONS": _V10Review_FACET_INSTRUCTIONS,
        "_V10Review_OBJECTION_REASONS": _V10Review_OBJECTION_REASONS,
        "_V10Review_REVIEW_INSTRUCTIONS": _V10Review_REVIEW_INSTRUCTIONS,
        "_V10Review_VISIBLE_BASIS": _V10Review_VISIBLE_BASIS,
        "_V10Review__check_projection": _V10Review__check_projection,
        "_V10Review__evidence": _V10Review__evidence,
        "_V10Review__facet_names": _V10Review__facet_names,
        "_V10Review__objections": _V10Review__objections,
        "_V10Review__strings": _V10Review__strings,
        "_V10Review__typed_projection": _V10Review__typed_projection,
        "_V10Review_blind_challenge_payload": _V10Review_blind_challenge_payload,
        "_V10Review_conclusive_rejection_ids": _V10Review_conclusive_rejection_ids,
        "_V10Review_copy": _V10Review_copy,
        "_V10Review_facet_admission_ids": _V10Review_facet_admission_ids,
        "_V10Review_route_issues": _V10Review_route_issues,
        "_V10Review_validate_facet_admission": _V10Review_validate_facet_admission,
        "_V10V2_ADMISSION_INSTRUCTIONS": _V10V2_ADMISSION_INSTRUCTIONS,
        "_V10V2_BASE_POLICY": _V10V2_BASE_POLICY,
        "_V10V2_BRIEF_INSTRUCTIONS": _V10V2_BRIEF_INSTRUCTIONS,
        "_V10V2_CHECK_INSTRUCTIONS": _V10V2_CHECK_INSTRUCTIONS,
        "_V10V2_ClarificationAlgorithmBase": _V10V2_ClarificationAlgorithmBase,
        "_V10V2_DIAGNOSE_INSTRUCTIONS": _V10V2_DIAGNOSE_INSTRUCTIONS,
        "_V10V2_GROUNDING": _V10V2_GROUNDING,
        "_V10V2_IntentBridgeV2Clarifier": _V10V2_IntentBridgeV2Clarifier,
        "_V10V2_LimitsExceededException": _V10V2_LimitsExceededException,
        "_V10V2_MAX_CHECKS": _V10V2_MAX_CHECKS,
        "_V10V2_PLAN_INSTRUCTIONS": _V10V2_PLAN_INSTRUCTIONS,
        "_V10V2_PROBE_PREFIX": _V10V2_PROBE_PREFIX,
        "_V10V2_QUESTION_INSTRUCTIONS": _V10V2_QUESTION_INSTRUCTIONS,
        "_V10V2_REVIEW_INSTRUCTIONS": _V10V2_REVIEW_INSTRUCTIONS,
        "_V10V2_SOLVE_INSTRUCTIONS": _V10V2_SOLVE_INSTRUCTIONS,
        "_V10V2_TYPED_INSTRUCTIONS": _V10V2_TYPED_INSTRUCTIONS,
        "_V10V2_TYPE_NAMES": _V10V2_TYPE_NAMES,
        "_V10V2_TooManyQuestionException": _V10V2_TooManyQuestionException,
        "_V10V2__Run": _V10V2__Run,
        "_V10V2__input_ref": _V10V2__input_ref,
        "_V10V2__observation_typed": _V10V2__observation_typed,
        "_V10V2__signature": _V10V2__signature,
        "_V10V2_ast": _V10V2_ast,
        "_V10V2_copy": _V10V2_copy,
        "_V10V2_decode_typed": _V10V2_decode_typed,
        "_V10V2_hashlib": _V10V2_hashlib,
        "_V10V2_json": _V10V2_json,
        "_V10V2_keyword": _V10V2_keyword,
        "_V10V2_math": _V10V2_math,
        "_V10V2_parse_candidate": _V10V2_parse_candidate,
        "_V10V2_parse_observations": _V10V2_parse_observations,
        "_V10V2_probe_script": _V10V2_probe_script,
        "_V10V2_qa_hash": _V10V2_qa_hash,
        "_V10V2_re": _V10V2_re,
        "_V10V2_validate_brief": _V10V2_validate_brief,
        "_V10V2_validate_checks": _V10V2_validate_checks,
        "_V10V2_validate_evidence": _V10V2_validate_evidence,
        "_V10V2_validate_policy": _V10V2_validate_policy,
        "_V10V3_BRIEF_INSTRUCTIONS": _V10V3_BRIEF_INSTRUCTIONS,
        "_V10V3_CANDIDATE_REVIEW_INSTRUCTIONS": _V10V3_CANDIDATE_REVIEW_INSTRUCTIONS,
        "_V10V3_CHECK_OBJECT_SCHEMA": _V10V3_CHECK_OBJECT_SCHEMA,
        "_V10V3_DEFAULT_POLICY": _V10V3_DEFAULT_POLICY,
        "_V10V3_IntentBridgeV3Clarifier": _V10V3_IntentBridgeV3Clarifier,
        "_V10V3_REFERENCE_INSTRUCTIONS": _V10V3_REFERENCE_INSTRUCTIONS,
        "_V10V3__Run": _V10V3__Run,
        "_V10V3_copy": _V10V3_copy,
        "_V10V3_json": _V10V3_json,
        "_V10V3_keyword": _V10V3_keyword,
        "_V10V4_COMPLETION_INSTRUCTIONS": _V10V4_COMPLETION_INSTRUCTIONS,
        "_V10V4_DEFAULT_POLICY": _V10V4_DEFAULT_POLICY,
        "_V10V4_IntentBridgeV4Clarifier": _V10V4_IntentBridgeV4Clarifier,
        "_V10V4__Run": _V10V4__Run,
        "_V10V4_copy": _V10V4_copy,
        "_V10V4_json": _V10V4_json,
        "_V10V4_keyword": _V10V4_keyword,
        "_V10V5_COVERAGE_INSTRUCTIONS": _V10V5_COVERAGE_INSTRUCTIONS,
        "_V10V5_DECISION_INSTRUCTIONS": _V10V5_DECISION_INSTRUCTIONS,
        "_V10V5_DEFAULT_POLICY": _V10V5_DEFAULT_POLICY,
        "_V10V5_IntentBridgeV5Clarifier": _V10V5_IntentBridgeV5Clarifier,
        "_V10V5_QUESTION_INSTRUCTIONS": _V10V5_QUESTION_INSTRUCTIONS,
        "_V10V5__Run": _V10V5__Run,
        "_V10V5_copy": _V10V5_copy,
        "_V10V5_keyword": _V10V5_keyword,
        "_V10Visible_DERIVATION": _V10Visible_DERIVATION,
        "_V10Visible__call": _V10Visible__call,
        "_V10Visible__comparison": _V10Visible__comparison,
        "_V10Visible__data_ranges": _V10Visible__data_ranges,
        "_V10Visible__literal": _V10Visible__literal,
        "_V10Visible__node_span": _V10Visible__node_span,
        "_V10Visible__offsets": _V10Visible__offsets,
        "_V10Visible__typed": _V10Visible__typed,
        "_V10Visible_ast": _V10Visible_ast,
        "_V10Visible_copy": _V10Visible_copy,
        "_V10Visible_doctest": _V10Visible_doctest,
        "_V10Visible_extract_visible_examples": _V10Visible_extract_visible_examples,
        "_V10Visible_hashlib": _V10Visible_hashlib,
        "_V10Visible_json": _V10Visible_json,
        "_V10Visible_math": _V10Visible_math,
        "_V10Visible_re": _V10Visible_re,
        "entry": IntentBridgeComponentClarifier,
    }


implementationSymbols = createImplementation()
IntentBridgeComponentClarifier = implementationSymbols.pop("entry")
