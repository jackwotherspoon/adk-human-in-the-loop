# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import asyncio

import httpx

from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.tools import FunctionTool, ToolContext

async def prepare_approval(tool_context: ToolContext, amount: float, reason: str) -> dict:
    """Prepare the approval request details based on user input.
    
    Args:
        tool_context (ToolContext): The tool context
        amount (float): The amount to approve
        reason (str): The reason for the approval
    
    Returns:
        dict: The approval request details
    """
    async with httpx.AsyncClient() as client:
        # First post the request
        response = await client.post(
            "http://localhost:9000/request",
            json={"amount": amount, "reason": reason}
        )
        # Error if not 200
        response.raise_for_status()
        request_data = response.json()
        tool_context.state["approval_request_id"] = request_data["id"]
        tool_context.state["approval_amount"] = amount
        tool_context.state["approval_reason"] = reason
        return {
            "status": "Successfully prepared approval request",
            "approval_request_id": request_data["id"],
            "approval_amount": amount,
            "approval_reason": reason,
        }

    
async def external_approval_tool(tool_context: ToolContext) -> str:
    """External approval tool
    
    Args:
        tool_context (ToolContext): The tool context
    
    Returns:
        str: The approval status
    """
    request_id = tool_context.state["approval_request_id"]
    async with httpx.AsyncClient() as client:
        # Poll for status
        while True:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"http://localhost:9000/request/{request_id}")
                # Error if not 200
                response.raise_for_status()
                status_data = response.json()
                if status_data["status"] != "pending":
                    return status_data["status"]
            await asyncio.sleep(10)
    
prepare_approval_tool = FunctionTool(func=prepare_approval)
approval_tool = FunctionTool(func=external_approval_tool)

# Agent that prepares the request
prepare_request = LlmAgent(
    model="gemini-2.5-pro-preview-05-06",
    name="PrepareApproval",
    instruction="Prepare the approval request details based on user input. Store amount and reason in state.",
    tools=[prepare_approval_tool],
)

# Agent that calls the human approval tool
request_approval = LlmAgent(
    model="gemini-2.5-pro-preview-05-06",
    name="RequestHumanApproval",
    instruction="Use the external_approval_tool with approval_request_id from state['approval_request_id'].",
    tools=[approval_tool],
    output_key="human_decision"
)

# Agent that proceeds based on human decision
process_decision = LlmAgent(
    model="gemini-2.5-pro-preview-05-06",
    name="ProcessDecision",
    instruction="Check state key 'human_decision'. If 'approved', proceed. If 'rejected', inform user."
)

root_agent = SequentialAgent(
    name="HumanApprovalWorkflow",
    sub_agents=[prepare_request, request_approval, process_decision]
)