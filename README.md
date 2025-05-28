# ADK Human-in-the-Loop Example

This is a simple example of using the ADK to create a human-in-the-loop workflow.

In this example we will use a human-in-the-loop workflow to send an expense request for manager approval. The agent then waits until the manager approves or rejects the request before proceeding.


## Running the Example

We will use a FastAPI server to handle the expense requests and a Streamlit app to display the pending requests as a manager approval dashboard.

### Start the FastAPI server

The FastAPI server provides basic CRUD operations for the expense requests and stores them in memory in a dictionary.

```bash
uv run server.py
```

The server is now running on `localhost:9000` and provides a REST API for the expense requests.

### Start the Streamlit app

The Streamlit app will display all pending expense requests and allow the manager to approve or reject them.

```bash
uv run streamlit run client.py
```

The Streamlit app is now running on `localhost:8501` and displays a manager approval dashboard.

![Streamlit App](streamlit_app.png)


### Start the ADK agent

```bash
uv run adk web
```

Navigate to `localhost:8000` in your browser to access the ADK web interface.

Go ahead and type something like `Amount 500, reason "team dinner"`.

You should see the agent call the `prepare_approval` tool which creates a new expense request and posts it to the FastAPI server. 

The agent then waits for the manager to approve or reject the request. This is done by calling the `external_approval_tool` tool which polls the FastAPI server for the request status every 30 seconds until the request is no longer `pending` (approved or rejected).

To approve or reject the request, head to the Streamlit app at `localhost:8501` in your browser and click the `Approve` or `Reject` button for the given expense ID.

![Pending Expense](pending_expense.png)

Hit `Reject` or `Approve` and wait for the agent to poll the FastAPI server for the request status.

Once it does so it should respond accordingly based on the human-in-the-loop decision!

![ADK Web Interface](adk_web_interface.png)
