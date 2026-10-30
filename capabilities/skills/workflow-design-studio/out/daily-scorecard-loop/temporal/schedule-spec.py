# DRAFT Temporal schedule registration for daily-scorecard-loop (workflow-design-studio)
# Shape mirrors ~/.rig/runtimes/temporal-runners/lane_schedules.py. NOTHING REGISTERED.
# from temporalio.client import Schedule, ScheduleActionStartWorkflow, ScheduleSpec, ScheduleState
# sid = "wds-daily-scorecard-loop-v1"
# Schedule(
#     action=ScheduleActionStartWorkflow(<workflow>, id="wds-daily-scorecard-loop-v1", task_queue="<queue>",
#                                        execution_timeout=timedelta(minutes=<budget>)),
#     spec=ScheduleSpec(cron_expressions=["3 7 * * 1,2,3,4,5"], time_zone_name="America/Denver"),
#     state=ScheduleState(paused=True, note="DRAFT workflow-design-studio; unpause is a Gate-D action"),
# )
