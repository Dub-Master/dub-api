## Dub-master API

#### Local Development setup

`python -m venv venv`
`source venv/bin/activate`
`pip install -r requirements.txt`

Run the API: `uvicorn main:app --reload`

#### Folder structure

```
- pipeline
    - workers
        - worker_1
            - activities.py (includes activity A, B, C)
            - workflows.py (includes workflows based on the worker_1 activities)
            - run_worker_1.py (starts worker for worker_1 related tasks, referencing the activities)
        - worker_2
            - activities.py (includes activities D, E)
            - workflows.py (includes workflows based on the worker_2 activities)
            - run_worker_2.py (starts worker for worker_2 related tasks, referencing the activities)
        - common
            - helpers.py (shared modules/helpers)
            - models.py (Data models if used)
        - run_workflow.py (combined file to start different workflows for your application)
```
