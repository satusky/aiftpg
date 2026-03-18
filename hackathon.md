You are a research software developer coordinating a hackathon. Teams will be creating analytical pipelines in Python for extracting information from text, and then comparing their results to a ground truth. Your tasks are as follows:

1. Create a FAST API server that will receive submissions from the team.
- Submissions will be JSON objects with these core fields:
```
{
    "team_name": string,
    "variable_id": int,
    "extracted_values": {
        document_id: value
    },
}
```
- Extracted values will be a dictionary linking document ids to the extracted value
- Fields may be added to the submission structure, but they should always contain the core ones
- Subsequent successful submissions for each variable from a team should be tracked so that the ground truth comparison can be tracked over time for each variable and team
- Fully document the API

2. Create functions for hackathon organizers to easily construct the ground truth corpus.
- Ingest data from a CSV or JSON

3. Create functions for comparing the submissions to the ground truth.
- Use metrics that make sense (e.g. accuracy, precision, recall, ...)

4. Create a web dashboard.
- A leaderboard that breaks down the team scores and rankings for each variable using the highest score a team has submitted (which may not be the most recent)
- Team breakdowns for each variable that show the scores over time
