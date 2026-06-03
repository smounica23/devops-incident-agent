from langgraph.graph import StateGraph, END
from agent.state import IncidentState
from agent.nodes.alert_intake import alert_intake
from agent.nodes.log_investigation import log_investigation
from agent.nodes.metrics_investigation import metrics_investigation
from agent.nodes.trace_investigation import trace_investigation
from agent.nodes.deployment_investigation import deployment_investigation
from agent.nodes.pr_commit_analysis import pr_commit_analysis
from agent.nodes.root_cause_reasoning import root_cause_reasoning
from agent.nodes.fix_planner import fix_planner
from agent.nodes.code_fix import code_fix
from agent.nodes.branch_and_pr import branch_and_pr
from agent.nodes.human_approval import human_approval
from agent.nodes.merge import merge
from agent.nodes.escalate import escalate
from agent.nodes.confluence_documentation import confluence_documentation
from agent.nodes.teams_notification import teams_notification


def should_retry(state:IncidentState):
    if state.get("confidence_score", 10) < 6 and state.get("retry_count", 0) < 2:
        return "retry"
    return "complete"

def humanApprovalStatus(state: IncidentState):
    approval = state.get("approval_status")
    if approval == "approved":
        return "approved"
    elif approval in ["rejected", "timeout"]:
        return "rejected"
    elif approval == "request_changes":
        return "request_changes"
    else:
        return "rejected" 
    

def build_workflow():

    graph = StateGraph(IncidentState)

    graph.add_node("alert_intake",alert_intake)
    graph.add_node("log_investigation",log_investigation)
    graph.add_node("metrics_investigation",metrics_investigation)
    graph.add_node("trace_investigation",trace_investigation)
    graph.add_node("deployment_investigation",deployment_investigation)
    graph.add_node("pr_commit_analysis",pr_commit_analysis)
    graph.add_node("root_cause_reasoning",root_cause_reasoning)
    graph.add_node("fix_planner",fix_planner)
    graph.add_node("code_fix",code_fix)
    graph.add_node("branch_and_pr",branch_and_pr)
    graph.add_node("human_approval",human_approval)
    graph.add_node("merge",merge)
    graph.add_node("escalate",escalate)
    graph.add_node("confluence_documentation",confluence_documentation)
    graph.add_node("teams_notification",teams_notification)

    graph.set_entry_point("alert_intake")

    graph.add_edge("alert_intake", "log_investigation")
    graph.add_edge("log_investigation", "metrics_investigation")
    graph.add_edge("metrics_investigation", "trace_investigation")
    graph.add_edge("trace_investigation", "deployment_investigation")
    graph.add_edge("deployment_investigation", "pr_commit_analysis")
    graph.add_edge("pr_commit_analysis", "root_cause_reasoning")

    graph.add_conditional_edges("root_cause_reasoning", should_retry, {
        "retry" : "log_investigation",
        "complete": "fix_planner"
    })

    graph.add_edge("fix_planner", "code_fix")
    graph.add_edge("code_fix", "branch_and_pr")
    graph.add_edge("branch_and_pr", "human_approval")
    graph.add_conditional_edges("human_approval", humanApprovalStatus, {
        "approved" : "merge",
        "rejected" : "escalate",
        "request_changes" : "fix_planner"
    })
    graph.add_edge("escalate", END)
    graph.add_edge("merge", "confluence_documentation")
    graph.add_edge("confluence_documentation", "teams_notification")
    graph.add_edge("teams_notification", END)
    return graph.compile()

workflow = build_workflow()