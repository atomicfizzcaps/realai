"""Task graph executor (planner -> worker -> critic -> synthesizer)."""

from typing import Any, Dict, List


class TaskExecutor:
    def __init__(self, planner, worker, critic, synthesizer):
        self.planner = planner
        self.worker = worker
        self.critic = critic
        self.synthesizer = synthesizer

    def run(self, messages, context):
        plan_data = self.planner.step(messages, context)
        steps = plan_data.get("plan", [])
        if not isinstance(steps, list):
            steps = [str(steps)]
        context["plan"] = steps

        results: List[Dict[str, Any]] = []
        for step in steps:
            context["current_step"] = step
            worker_out = self.worker.step(messages, context)
            results.append({"step": step, "worker": worker_out})

            context["worker_output"] = worker_out
            critique = self.critic.step(messages, context)
            results.append({"step": step, "critique": critique})

        context["results"] = results
        final = self.synthesizer.step(messages, context)
        return {
            "plan": steps,
            "results": results,
            "final": final.get("final", ""),
        }

