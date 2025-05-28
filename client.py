import streamlit as st
import requests

st.title("Request Manager")

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
                if st.button("Approve", key=f"approve_{request['id']}"):
                    requests.put(f"http://localhost:9000/request/{request['id']}", json={"status": "approved"})
            with col2:
                if st.button("Reject", key=f"reject_{request['id']}"):
                    requests.put(f"http://localhost:9000/request/{request['id']}", json={"status": "rejected"})

    # Add a refresh button
    if st.button("Refresh"):  # Refresh button
        st.rerun()
