"""
arifos/runtime/wawa.py — WAWA: Wide Academic Wisdom Assistant
arifOS MCP Student Domain Skill

Adds WAWA student-domain prompts and resources to the arifOS MCP kernel.
Student data is governed by F1-F13 with enhanced F7 (Humility/data minimisation)
and F13 (Sovereign/student-owns-data) enforcement.

DITEMPA BUKAN DIBERI
"""

from __future__ import annotations
from typing import Any

from fastmcp import FastMCP

# =============================================================================
# WAWA PROMPT SPECS — matches WAWA/mcp/prompts/*.md
# =============================================================================

WAWA_PROMPT_SPECS: list[dict[str, Any]] = [
    {
        "name": "wawa.timetable_guardian",
        "description": (
            "Parse, store, and remind a student's class schedule. "
            "Enforces: F4 Clarity (plain output), F5 Peace² (calm reminders), "
            "F7 Humility (minimum data), F11 Auditability (log to VAULT999)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["ADD", "REMOVE", "VIEW", "CHECK_TODAY", "CHECK_TOMORROW", "CONFLICT_SCAN"],
                },
                "class_data": {
                    "type": "object",
                    "properties": {
                        "subject_code": {"type": "string", "description": "e.g. SOS3002"},
                        "subject_name": {"type": "string"},
                        "day": {"type": "string", "enum": ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]},
                        "start_time": {"type": "string", "description": "HH:MM"},
                        "end_time": {"type": "string", "description": "HH:MM"},
                        "room": {"type": "string"},
                        "lecturer": {"type": "string"},
                    },
                    "required": ["subject_code", "subject_name", "day", "start_time", "end_time", "room"],
                },
            },
            "required": ["action"],
        },
    },
    {
        "name": "wawa.deadline_engine",
        "description": (
            "Track assignment deadlines with proactive 3-day escalation reminders. "
            "Enforces: F2 Truth (confirmed deadlines only), F5 Peace² (supportive tone), "
            "F8 Genius (minimal effort to add), F11 Auditability, F13 Sovereign (student controls data)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["ADD", "LIST", "CHECK", "COMPLETE", "OVERDUE_SCAN"],
                },
                "deadline": {
                    "type": "object",
                    "properties": {
                        "subject_code": {"type": "string"},
                        "title": {"type": "string"},
                        "due_date": {"type": "string", "description": "YYYY-MM-DD or YYYY-MM-DDTHH:MM"},
                        "priority": {"type": "string", "enum": ["LOW", "MED", "HIGH", "URGENT"]},
                        "description": {"type": "string"},
                        "submission_link": {"type": "string"},
                    },
                    "required": ["subject_code", "title", "due_date", "priority"],
                },
            },
            "required": ["action"],
        },
    },
    {
        "name": "wawa.lecture_companion",
        "description": (
            "Store, summarise, and retrieve lecture notes. "
            "Enforces: F4 Clarity (searchable output), F7 Humility (summarise, don't retain raw unless needed), "
            "F11 Auditability (log note additions)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["ADD", "SUMMARISE", "SEARCH", "RETRIEVE", "LIST"],
                },
                "subject_code": {"type": "string"},
                "title": {"type": "string"},
                "content": {"type": "string", "description": "Raw note content or lecture transcript"},
                "topics": {"type": "array", "items": {"type": "string"}, "description": "Key topics covered"},
            },
            "required": ["action", "subject_code"],
        },
    },
    {
        "name": "wawa.group_hub",
        "description": (
            "Coordinate group project members, track individual contributions, surface accountability gaps. "
            "Enforces: F4 Clarity (neutral factual language), F5 Peace² (no blame), "
            "F9 Anti-Hantu (no fabricated progress), F11 Auditability."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["CREATE", "ADD_MEMBER", "ADD_TASK", "UPDATE_TASK", "VIEW_BOARD", "MEMBER_REPORT"],
                },
                "project": {
                    "type": "object",
                    "properties": {
                        "project_id": {"type": "string"},
                        "project_name": {"type": "string"},
                        "subject_code": {"type": "string"},
                        "deadline": {"type": "string"},
                        "members": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "student_id": {"type": "string"},
                                    "name": {"type": "string"},
                                    "role": {"type": "string"},
                                },
                            },
                        },
                        "tasks": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "task_id": {"type": "string"},
                                    "title": {"type": "string"},
                                    "assigned_to": {"type": "string"},
                                    "status": {"type": "string", "enum": ["TODO", "IN_PROGRESS", "DONE"]},
                                    "due_date": {"type": "string"},
                                },
                            },
                        },
                    },
                },
            },
            "required": ["action"],
        },
    },
    {
        "name": "wawa.exam_prep",
        "description": (
            "Identify weak areas from quiz results, generate targeted quizzes per subject. "
            "Enforces: F2 Truth (based on actual quiz results), F4 Clarity, "
            "F8 Genius (maximum insight from quiz data)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["IDENTIFY_WEAK", "GENERATE_QUIZ", "TRACK_PROGRESS"],
                },
                "subject_code": {"type": "string"},
                "quiz_results": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "topic": {"type": "string"},
                            "score": {"type": "number", "description": "0.0 to 1.0"},
                            "date": {"type": "string"},
                        },
                    },
                },
                "question_count": {"type": "integer", "default": 10},
            },
            "required": ["action", "subject_code"],
        },
    },
    {
        "name": "wawa.wellness_check",
        "description": (
            "Monitor class attendance patterns, send wellbeing nudges when anomalies detected. "
            "Enforces: F5 Peace² (gentle supportive language), F6 Empathy (acknowledge stress first), "
            "F11 Auditability (log attendance patterns), 888_HOLD before escalation to human."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["LOG_ATTENDANCE", "WELLNESS_SCAN", "SEND_NUDGE", "WELLNESS_REPORT"],
                },
                "student_id": {"type": "string"},
                "subject_code": {"type": "string"},
                "status": {"type": "string", "enum": ["PRESENT", "ABSENT", "EXCUSED"]},
                "notes": {"type": "string"},
            },
            "required": ["action", "student_id"],
        },
    },
]

# =============================================================================
# WAWA RESOURCE DATA
# =============================================================================

WAWA_STUDENT_SCHEMA: dict[str, Any] = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "wawa://schema/student",
    "title": "WAWA Student Profile",
    "description": "Core student data schema for WAWA personal academic OS",
    "type": "object",
    "properties": {
        "student_id": {"type": "string", "format": "uuid", "description": "F13 sovereign — student owns this"},
        "name": {"type": "string"},
        "university": {"type": "string"},
        "programme": {"type": "string"},
        "intake_year": {"type": "integer"},
        "language_pref": {"type": "string", "enum": ["BM", "EN", "MIXED"], "default": "MIXED"},
        "mcp_session_id": {"type": "string", "format": "uuid"},
        "subjects": {"type": "array", "items": {"$ref": "#/definitions/Subject"}},
        "deadlines": {"type": "array", "items": {"$ref": "#/definitions/Deadline"}},
        "group_projects": {"type": "array", "items": {"$ref": "#/definitions/GroupProject"}},
    },
    "required": ["student_id", "name", "university", "programme"],
    "definitions": {
        "Subject": {
            "type": "object",
            "properties": {
                "subject_id": {"type": "string", "format": "uuid"},
                "subject_code": {"type": "string", "pattern": "^[A-Z]{2,4}[0-9]{4}$"},
                "subject_name": {"type": "string"},
                "lecturer": {"type": "string"},
                "timetable": {
                    "type": "array",
                    "items": {
                        "properties": {
                            "day": {"enum": ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]},
                            "start_time": {"pattern": "^([01]?[0-9]|2[0-3]):[0-5][0-9]$"},
                            "end_time": {"pattern": "^([01]?[0-9]|2[0-3]):[0-5][0-9]$"},
                            "room": {"type": "string"},
                        },
                        "required": ["day", "start_time", "end_time"],
                    },
                },
            },
            "required": ["subject_id", "subject_code", "subject_name"],
        },
        "Deadline": {
            "type": "object",
            "properties": {
                "deadline_id": {"type": "string", "format": "uuid"},
                "subject_id": {"type": "string"},
                "title": {"type": "string"},
                "due_date": {"type": "string", "format": "date-time"},
                "priority": {"enum": ["LOW", "MED", "HIGH", "URGENT"]},
                "status": {"enum": ["PENDING", "IN_PROGRESS", "DONE", "OVERDUE"]},
                "reminder_log": {"type": "array", "items": {"type": "string", "format": "date-time"}},
            },
            "required": ["deadline_id", "subject_id", "title", "due_date", "priority", "status"],
        },
        "GroupProject": {
            "type": "object",
            "properties": {
                "project_id": {"type": "string", "format": "uuid"},
                "project_name": {"type": "string"},
                "subject_id": {"type": "string"},
                "members": {
                    "type": "array",
                    "items": {
                        "properties": {"student_id": {"type": "string"}, "name": {"type": "string"}, "role": {"type": "string"}},
                        "required": ["student_id", "name"],
                    },
                },
                "tasks": {
                    "type": "array",
                    "items": {
                        "properties": {
                            "task_id": {"type": "string"},
                            "title": {"type": "string"},
                            "assigned_to": {"type": "string"},
                            "status": {"enum": ["TODO", "IN_PROGRESS", "DONE"]},
                        },
                        "required": ["task_id", "title", "assigned_to", "status"],
                    },
                },
            },
            "required": ["project_id", "project_name", "subject_id", "members", "tasks"],
        },
    },
}

# =============================================================================
# WAWA CONSTITUTIONAL OVERLAY — student-specific floor emphasis
# =============================================================================

WAWA_FLOOR_OVERLAY: dict[str, dict[str, Any]] = {
    "F7_emphasis": {
        "name": "WAWA_DATA_MINIMISATION",
        "principle": "Keep only what is necessary for the student's benefit",
        "question": "Does WAWA really need this data point to serve the student?",
        "action": "If not strictly necessary → do not store. Do not log. Do not retain.",
        "floor": "F7",
    },
    "F13_emphasis": {
        "name": "WAWA_SOVEREIGN",
        "principle": "Student is always the final authority on their academic data",
        "question": "Has the student explicitly authorized this data use?",
        "action": "No data sharing, no third-party access, no model training without explicit student consent.",
        "floor": "F13",
    },
    "F5_emphasis": {
        "name": "WAWA_PEACE",
        "principle": "Academic stress is real — WAWA must never add to it",
        "question": "Is this reminder or message calm, supportive, and constructive?",
        "action": "If language could increase anxiety → rewrite to empathetic, solution-forward tone.",
        "floor": "F5",
    },
    "F9_emphasis": {
        "name": "WAWA_ANTI_HANTU",
        "principle": "WAWA never fabricates deadlines, attendance, or progress",
        "question": "Is this reminder grounded in confirmed data?",
        "action": "Never send a reminder based on inference. Only confirmed data triggers alerts.",
        "floor": "F9",
    },
}

# =============================================================================
# WAWA ESCALATION RULES
# =============================================================================

WAWA_ESCALATION_MATRIX: list[dict[str, Any]] = [
    {
        "condition": "deadline OVERDUE + 1 day",
        "prompt": "wawa.deadline_engine",
        "action": "NUDGE",
        "tone": "supportive",
        "escalate_after_days": 3,
    },
    {
        "condition": "3+ tasks OVERDUE in group project, same member",
        "prompt": "wawa.group_hub",
        "action": "INDIVIDUAL_NUDGE",
        "tone": "gentle",
        "escalate_after_days": 2,
    },
    {
        "condition": "Group 50%+ tasks overdue",
        "prompt": "wawa.group_hub",
        "action": "GROUP_ALERT",
        "tone": "factual",
        "requires_HOLD": True,
    },
    {
        "condition": "3+ consecutive class ABSENT without explanation",
        "prompt": "wawa.wellness_check",
        "action": "WELLNESS_NUDGE",
        "tone": "caring",
        "requires_HOLD": True,
    },
    {
        "condition": "888_HOLD — high-risk wellness flag",
        "prompt": "arifos.hold_gate",
        "action": "ESCALATE_TO_HUMAN",
        "requires_HUMAN": True,
    },
]

# =============================================================================
# REGISTER WAWA INTO ARIFOS MCP
# =============================================================================

def register_wawa_prompts(mcp: FastMCP) -> list[str]:
    """
    Register all WAWA prompts on the arifOS MCP instance.
    Call from server.py alongside register_v2_prompts().
    """
    registered = []

    # ── wawa.timetable_guardian ──────────────────────────────────────────────
    @mcp.prompt("wawa.timetable_guardian")
    def wawa_timetable_guardian(action: str, class_data: dict = None) -> str:
        """
        WAWA Timetable Guardian — student class schedule management.
        F4: plain output | F5: calm reminders | F7: minimum data | F11: log to vault
        """
        base = (
            "You are WAWA Timetable Guardian — part of WAWA, the Wide Academic Wisdom Assistant.\n"
            "Your role: help university students manage their class schedules proactively.\n\n"
            "CONSTITUTIONAL REMINDER: Apply F4 (clarity), F5 (calm tone), F7 (minimum data needed), "
            "F11 (log actions). Student data is sovereign — F13 always active.\n\n"
        )
        templates = {
            "ADD": (
                f"{base}"
                "TASK: Add a new class to the student's timetable.\n"
                "INPUT: action=ADD, class_data={class_data}\n\n"
                "Respond with:\n"
                "🗓️ **Class Added**\n"
                "[subject_code] — [subject_name]\n"
                "[day] · [start_time]–[end_time] · [room]\n"
                "Reminder set: 15 minutes before class.\n\n"
                "Also log to VAULT999: action=timetable_add, subject_code, timestamp."
            ),
            "VIEW": (
                f"{base}"
                "TASK: Display the student's full weekly timetable.\n"
                "Respond with a formatted weekly view, day by day.\n\n"
                "Also log to VAULT999: action=timetable_view, timestamp."
            ),
            "CHECK_TODAY": (
                f"{base}"
                "TASK: Show what classes the student has today.\n"
                "If no classes → acknowledge cheerfully: 'No classes today. Rest well — you've earned it.'\n"
                "If classes → show: subject, time, room, pre-class prep note if any.\n\n"
                "Log: action=timetable_check_today."
            ),
            "CHECK_TOMORROW": (
                f"{base}"
                "TASK: Show what classes the student has tomorrow.\n"
                "If classes → show with reminder: 'See you at [time] in [room]!'\n\n"
                "Log: action=timetable_check_tomorrow."
            ),
            "CONFLICT_SCAN": (
                f"{base}"
                "TASK: Scan for schedule conflicts (same time different rooms, less than 30min between classes far apart).\n"
                "If conflict found → warn clearly with resolution suggestion.\n"
                "If clean → report: 'No conflicts detected.'\n\n"
                "Log: action=timetable_conflict_scan."
            ),
        }
        return templates.get(action, templates["VIEW"]).format(class_data=class_data or {})

    # ── wawa.deadline_engine ─────────────────────────────────────────────────
    @mcp.prompt("wawa.deadline_engine")
    def wawa_deadline_engine(action: str, deadline: dict = None) -> str:
        """
        WAWA Deadline Engine — proactive assignment tracking with 3-day escalation.
        F2: confirmed deadlines only | F5: supportive tone | F8: minimal effort | F11+F13: vault + sovereign
        """
        base = (
            "You are WAWA Deadline Engine — part of WAWA, the Wide Academic Wisdom Assistant.\n"
            "Your role: track university assignment deadlines and send proactive escalation reminders.\n\n"
            "ESCALATION SCHEDULE: T-7 (info) → T-3 (nudge) → T-1 (final warning) → T-0 (day-of) → T+1 (overdue help)\n\n"
            "CONSTITUTIONAL REMINDER: F2 (truth — only confirmed deadlines), F5 (calm supportive language), "
            "F8 (minimise student effort to add), F11 (log all), F13 (student owns their data).\n\n"
        )
        templates = {
            "ADD": (
                f"{base}"
                "TASK: Add a new deadline to the student's tracker and activate escalation chain.\n"
                "INPUT: action=ADD, deadline={deadline}\n\n"
                "Respond with:\n"
                "⏱️ **Deadline Added**\n"
                "[title] — [subject_code]\n"
                "Due: [due_date] ([time_remaining])\n"
                "Priority: [priority]\n\n"
                "Reminder chain activated. WAWA will nudge at T-7, T-3, T-1, and T-0.\n\n"
                "Log to VAULT999: action=deadline_add, title, subject_code, due_date, priority."
            ),
            "LIST": (
                f"{base}"
                "TASK: Show all upcoming deadlines, sorted by due date.\n"
                "Format: bullet list with T-minus countdown.\n"
                "If all clear → cheerful acknowledgement: 'All clear! No upcoming deadlines.'\n\n"
                "Log: action=deadline_list."
            ),
            "OVERDUE_SCAN": (
                f"{base}"
                "TASK: Scan for overdue items.\n"
                "For each overdue item: show title, how many days late, and a constructive suggestion.\n"
                "If 3+ overdue → trigger 888_HOLD for wellness check.\n\n"
                "Log: action=deadline_overdue_scan."
            ),
        }
        return templates.get(action, templates["LIST"]).format(deadline=deadline or {})

    # ── wawa.group_hub ────────────────────────────────────────────────────────
    @mcp.prompt("wawa.group_hub")
    def wawa_group_hub(action: str, project: dict = None) -> str:
        """
        WAWA Group Hub — group project coordination with accountability tracking.
        F4: neutral factual language | F5: no blame | F9: no fabricated progress | F11: log
        """
        base = (
            "You are WAWA Group Hub — part of WAWA, the Wide Academic Wisdom Assistant.\n"
            "Your role: coordinate group project members and track individual contributions.\n\n"
            "CONSTITUTIONAL REMINDER: F4 (neutral factual language), F5 (never blame individuals — "
            "frame delays as 'opportunities to contribute'), F9 (never fabricate progress), "
            "F11 (log all board changes). F13: individual reports are private to that student.\n\n"
        )
        templates = {
            "CREATE": (
                f"{base}"
                "TASK: Create a new group project board.\n"
                "INPUT: action=CREATE, project={project}\n\n"
                "Respond with confirmation of board creation and member list.\n\n"
                "Log to VAULT999: action=group_create, project_name, member_count."
            ),
            "VIEW_BOARD": (
                f"{base}"
                "TASK: Display the full project kanban board.\n"
                "Format: 3 columns (TODO | IN PROGRESS | DONE), each task with assignee and due date.\n"
                "Show completion percentage at top.\n\n"
                "Log: action=group_view_board."
            ),
            "MEMBER_REPORT": (
                f"{base}"
                "TASK: Generate a private accountability report for one member.\n"
                "This report is for the member only — do NOT share with the group.\n"
                "Show: tasks assigned, tasks completed, tasks overdue, suggested next steps.\n"
                "Tone: supportive accountability partner, not supervisor.\n\n"
                "Log to VAULT999: action=group_member_report (private — student_id only)."
            ),
        }
        return templates.get(action, templates["VIEW_BOARD"]).format(project=project or {})

    # ── wawa.lecture_companion ───────────────────────────────────────────────
    @mcp.prompt("wawa.lecture_companion")
    def wawa_lecture_companion(action: str, subject_code: str, title: str = "", content: str = "", topics: list = None) -> str:
        """
        WAWA Lecture Companion — store, summarise, and retrieve lecture notes.
        F4: clarity | F7: minimise raw data retention | F11: log note additions
        """
        base = (
            "You are WAWA Lecture Companion — part of WAWA, the Wide Academic Wisdom Assistant.\n"
            "Your role: help students store, summarise, and retrieve their lecture materials.\n\n"
            "CONSTITUTIONAL REMINDER: F4 (clear searchable output), F7 (summarise — do not retain "
            "full raw content unless student explicitly requests it), F11 (log all note operations).\n\n"
        )
        templates = {
            "ADD": (
                f"{base}"
                "TASK: Add a new lecture note for {subject_code}.\n"
                "Title: {title}\n"
                "Topics: {topics}\n\n"
                "Summarise the content into clear bullet points (max 10 bullets). "
                "Store the summary linked to subject and topics.\n\n"
                "Log to VAULT999: action=note_add, subject_code, topic_count."
            ),
            "SEARCH": (
                f"{base}"
                "TASK: Search all notes for keyword or topic.\n"
                "Return matching notes with subject code, title, summary, and relevance score.\n\n"
                "Log: action=note_search."
            ),
            "RETRIEVE": (
                f"{base}"
                "TASK: Retrieve all notes for {subject_code}.\n"
                "Return as a clean, organised subject notebook.\n\n"
                "Log: action=note_retrieve."
            ),
        }
        return templates.get(action, templates["RETRIEVE"]).format(
            subject_code=subject_code, title=title or "Untitled", topics=topics or []
        )

    # ── wawa.exam_prep ──────────────────────────────────────────────────────
    @mcp.prompt("wawa.exam_prep")
    def wawa_exam_prep(action: str, subject_code: str, quiz_results: list = None, question_count: int = 10) -> str:
        """
        WAWA Exam Prep — AI quiz generation and weak area identification.
        F2: truth (based on actual results) | F8: maximum insight from minimal data
        """
        base = (
            "You are WAWA Exam Prep — part of WAWA, the Wide Academic Wisdom Assistant.\n"
            "Your role: help students prepare for exams by identifying weak areas and generating quizzes.\n\n"
            "CONSTITUTIONAL REMINDER: F2 (only use actual quiz data — do not fabricate scores), "
            "F8 (maximum insight from minimal input — make every quiz question count).\n\n"
        )
        templates = {
            "IDENTIFY_WEAK": (
                f"{base}"
                "TASK: Analyse quiz results and identify the student's weakest topics.\n"
                "INPUT: subject={subject_code}, quiz_results={quiz_results}\n\n"
                "Return: weak area ranked list + suggested study focus for each weak topic.\n\n"
                "Log: action=exam_identify_weak."
            ),
            "GENERATE_QUIZ": (
                f"{base}"
                "TASK: Generate {question_count} targeted quiz questions for {subject_code}.\n"
                "Focus on previously identified weak areas.\n"
                "Mix: multiple choice (60%), short answer (30%), case application (10%).\n\n"
                "Log: action=exam_generate_quiz, question_count."
            ),
        }
        return templates.get(action, templates["IDENTIFY_WEAK"]).format(
            subject_code=subject_code, quiz_results=quiz_results or [], question_count=question_count
        )

    # ── wawa.wellness_check ───────────────────────────────────────────────────
    @mcp.prompt("wawa.wellness_check")
    def wawa_wellness_check(action: str, student_id: str, subject_code: str = "", status: str = "", notes: str = "") -> str:
        """
        WAWA Wellness Check — attendance monitoring and wellbeing nudges.
        F5: caring tone | F6: acknowledge stress first | F11: log patterns | 888_HOLD before escalation
        """
        base = (
            "You are WAWA Wellness Check — part of WAWA, the Wide Academic Wisdom Assistant.\n"
            "Your role: monitor class attendance patterns and check in on student wellbeing.\n\n"
            "CONSTITUTIONAL REMINDER: F5 (gentle caring language), F6 (acknowledge academic stress "
            "before giving solutions), F11 (log attendance patterns). "
            "If 3+ consecutive absences → 888_HOLD before any escalation to human.\n\n"
        )
        templates = {
            "LOG_ATTENDANCE": (
                f"{base}"
                "TASK: Log a class attendance record.\n"
                "INPUT: student_id={student_id}, subject={subject_code}, status={status}, notes={notes}\n\n"
                "Respond with confirmation.\n"
                "If status=ABSENT → check if 3+ consecutive absences → set 888_HOLD flag.\n\n"
                "Log to VAULT999: action=wellness_log, student_id, subject, status."
            ),
            "WELLNESS_SCAN": (
                f"{base}"
                "TASK: Scan attendance pattern for {student_id}.\n"
                "If anomalies (3+ consecutive absences) → trigger wellness nudge.\n"
                "If persistent absence → escalate via 888_HOLD.\n\n"
                "Log: action=wellness_scan."
            ),
            "WELLNESS_REPORT": (
                f"{base}"
                "TASK: Generate a wellbeing summary for {student_id}.\n"
                "Show: classes attended, absences, overall engagement score.\n"
                "End with: 'How are you really doing?' — open-ended caring check-in.\n\n"
                "Log: action=wellness_report."
            ),
        }
        return templates.get(action, templates["WELLNESS_REPORT"]).format(
            student_id=student_id, subject_code=subject_code or "", status=status or "", notes=notes or ""
        )

    registered = [
        "wawa.timetable_guardian",
        "wawa.deadline_engine",
        "wawa.lecture_companion",
        "wawa.group_hub",
        "wawa.exam_prep",
        "wawa.wellness_check",
    ]
    return registered


def register_wawa_resources(mcp: FastMCP) -> list[str]:
    """
    Register WAWA-specific resources on the arifOS MCP instance.
    Call from server.py alongside register_v2_resources().
    """
    import json

    registered = []

    @mcp.resource("wawa://schema/student")
    def wawa_student_schema() -> str:
        """JSON Schema for WAWA student profile data model."""
        return json.dumps(WAWA_STUDENT_SCHEMA, indent=2)

    @mcp.resource("wawa://doctrine/student-floors")
    def wawa_floor_overlay() -> str:
        """WAWA-specific constitutional floor emphasis — student data governance."""
        lines = ["# WAWA Constitutional Floor Overlay\n"]
        lines.append("WAWA operates under full F1-F13, with these student-domain emphases:\n")
        for key, floor in WAWA_FLOOR_OVERLAY.items():
            lines.append(f"## {floor['name']} ({floor['floor']})\n")
            lines.append(f"**Principle:** {floor['principle']}\n")
            lines.append(f"**Question:** {floor['question']}\n")
            lines.append(f"**Action:** {floor['action']}\n\n")
        return "\n".join(lines)

    @mcp.resource("wawa://doctrine/escalation-matrix")
    def wawa_escalation_matrix() -> str:
        """WAWA escalation rules — when to nudge, when to HOLD, when to escalate to human."""
        import json
        return json.dumps(WAWA_ESCALATION_MATRIX, indent=2)

    @mcp.resource("wawa://doctype")
    def wawa_doctype() -> str:
        """WAWA definition document — what WAWA is, what it does, how it connects to arifOS MCP."""
        return """# WAWA — Wide Academic Wisdom Assistant
## arifOS MCP Student Domain Skill

**Full name:** Wide Academic Wisdom Assistant
**Domain:** Malaysian university student personal academic OS
**Runtime:** arifOS MCP kernel (mcp.arif-fazil.com)
**Motto:** DITEMPA BUKAN DIBERI

## What is WAWA?

WAWA gives every university student their own personal AI agent — not a chatbot you open,
but an agent that knows your timetable, deadlines, group projects, and study patterns,
and proactively sends you what you need before you ask.

**WAWA means "ours" (Swahili).** Here: your own, personal, always-on academic companion.

## Features

| Feature | Prompt | Description |
|---|---|---|
| Timetable Guardian | wawa.timetable_guardian | Parse, store, remind class schedules |
| Deadline Engine | wawa.deadline_engine | 3-day proactive escalation reminders |
| Lecture Companion | wawa.lecture_companion | Store, summarise, retrieve notes |
| Group Hub | wawa.group_hub | Project coordination + member accountability |
| Exam Prep | wawa.exam_prep | Quiz generation + weak area detection |
| Wellness Check | wawa.wellness_check | Attendance monitoring + wellbeing nudges |

## Constitutional Governance

WAWA inherits full F1-F13 from arifOS MCP, with student-domain overlays:

- **F7_emphasis**: DATA_MINIMISATION — keep only what serves the student
- **F13_emphasis**: SOVEREIGN — student always owns and controls their data
- **F5_emphasis**: PEACE — academic tone, never anxiety-inducing
- **F9_emphasis**: ANTI_HANTU — no fabricated reminders, only confirmed data

## Architecture

```
Student (Telegram / WhatsApp / Web)
    ↓
WAWA Prompt (wawa.*)
    ↓
arifOS MCP Kernel (F1-F13 enforcement)
    ↓
VAULT999 (student data, sealed append-only ledger)
```

## Connection

WAWA is NOT a separate MCP server. It is a skill layer registered on the arifOS MCP kernel.
Student agents connect once to mcp.arif-fazil.com and access WAWA prompts via the prompt endpoint.

**arifOS MCP connection string:**
```
npx @anthropic/mcp install wawa --url https://mcp.arif-fazil.com/mcp
```
"""

    registered = [
        "wawa://schema/student",
        "wawa://doctrine/student-floors",
        "wawa://doctrine/escalation-matrix",
        "wawa://doctype",
    ]
    return registered


__all__ = [
    "WAWA_PROMPT_SPECS",
    "WAWA_STUDENT_SCHEMA",
    "WAWA_FLOOR_OVERLAY",
    "WAWA_ESCALATION_MATRIX",
    "register_wawa_prompts",
    "register_wawa_resources",
]
