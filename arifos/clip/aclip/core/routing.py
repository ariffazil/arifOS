# Routing logic for pipeline progression

def next_stage(current_stage):
    """
    Determine the next stage number in the pipeline after current_stage.
    Skips the hold stage (888) in normal flow; hold is triggered only by issues.
    Returns the next stage number (int) or None if the pipeline is complete.
    """
    stage_order = [0, 111, 222, 333, 444, 555, 666, 777, 999]
    if current_stage in stage_order:
        idx = stage_order.index(current_stage)
        if idx < len(stage_order) - 1:
            return stage_order[idx + 1]
    return None
