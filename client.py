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

import streamlit as st
import requests

st.title("Expense Request Dashboard")

# Get expense requests from server
response = requests.get("http://localhost:9000/requests")
requests_data = response.json()

# Filter only pending requests
pending_requests = [req for req in requests_data if req["status"] == "pending"]

if not pending_requests:
    st.info("No pending requests to review")
else:
    for request in pending_requests:
        with st.expander(request["id"]):
            st.write(f"Amount: ${request['amount']:.2f}")
            st.write(f"Reason: {request['reason']}")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Approve", 
                           key=f"approve_{request['id']}", 
                           use_container_width=True, 
                           icon="✅",
                           help="Approve this request",
                ):
                    requests.put(f"http://localhost:9000/request/{request['id']}", json={"status": "approved"})
                    st.success("Request approved!")
                    st.rerun()
            with col2:
                if st.button("Reject", 
                           key=f"reject_{request['id']}", 
                           use_container_width=True, 
                           icon="❌",
                           help="Reject this request",
                ):
                    requests.put(f"http://localhost:9000/request/{request['id']}", json={"status": "rejected"})
                    st.error("Request rejected!")
                    st.rerun()
