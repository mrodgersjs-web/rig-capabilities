# Start in Hermes

Open Hermes with the installed workflow:

```sh
hermes --rig-task "Prepare resume-only job applications" --skills hermes-resume-only-applications --in "/Users/rig128gb/Desktop/Projects/rig-linkedin-studio-luca"
```

Paste PROMPT.md from this directory, then add the job URL or description. With no target supplied, the prompt inspects the current ApplyOps queue and prepares up to five suitable unsubmitted jobs. It does not submit or start a recurring schedule.

Quick prompt:

```text
Use the hermes-resume-only-applications skill. Follow its PROMPT.md and WORKFLOW.md, verify sources.json, and prepare the next five suitable jobs from my existing queue. My current selected resume is the only employment source. Answer No for direct prior-employer questions about companies absent from it; preserve supported answers to other questions and flag unknowns. Produce review packets and show any missing answers. Stop before final submission.
```

Source check:

```sh
python3 /Users/rig128gb/.hermes/skills/hermes-resume-only-applications/verify_sources.py
```

The source check is read-only and does not start inference or a browser. Browser prefill also requires a passing bsk doctor result; the current protocol mismatch is documented in DEPENDENCIES.md.
