import { existsSync, watch } from "node:fs";
import { reserveGlobalQuota } from "../src/extension";

const stateRoot = process.argv[2];
const startBarrier = process.argv[3];
if (!stateRoot || !startBarrier) throw new Error("state root and start barrier required");
console.log("READY");
if (!existsSync(startBarrier)) {
  await new Promise<void>((resolve) => {
    const watcher = watch(stateRoot, () => {
      if (!existsSync(startBarrier)) return;
      watcher.close();
      resolve();
    });
    if (existsSync(startBarrier)) {
      watcher.close();
      resolve();
    }
  });
}

const reservation = reserveGlobalQuota(
  { request: "race", response: "race", evidence: [] },
  {
    stateRoot,
    dailyBudgetUsd: 1,
    dailyMaxCalls: 2,
    inputPricePerMillionUsd: 0.042,
  },
  new Date("2026-09-16T21:00:00Z"),
);
console.log(JSON.stringify(reservation));
