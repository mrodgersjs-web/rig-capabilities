// Hook fail-closed tests — spawn failure must never map to exit 0 (admit).
// Run with: bun test tests/rig_prime_hook.test.ts
import { describe, expect, test } from "bun:test";
import { runGate } from "../capabilities/hooks/rig-prime.ts";

describe("runGate fail-closed", () => {
	test("ENOENT spawn failure maps to -1 with a surfaced message, never 0/admit", async () => {
		const previous = process.env.RIG_D85_CLI;
		process.env.RIG_D85_CLI = "/nonexistent/rig-determinism-85";
		try {
			const [code, out] = await runGate(["inventory", "julie_synthetic"]);
			expect(code).toBe(-1);
			expect(out).toContain("error:");
		} finally {
			if (previous === undefined) delete process.env.RIG_D85_CLI;
			else process.env.RIG_D85_CLI = previous;
		}
	});
});
