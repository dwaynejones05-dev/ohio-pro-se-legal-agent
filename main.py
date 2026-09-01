import os
from crewai import Agent, Crew, Process, Task

# Replace with your actual API key
os.environ["OPENAI_API_KEY"] = "your-api-key-here"

# 1. Define Specialized Agents
docket_auditor = Agent(
    role="Procedural & Docket Auditor",
    goal="Identify unrecorded hearings, missing transcripts, and statutory violations in juvenile court dockets.",
    backstory="You are a meticulous paralegal specializing in auditing trial court dockets for structural errors under Juv.R. 37(A) and App.R. 9(C).",
    verbose=True,
)

legal_writer = Agent(
    role="Appellate Brief Specialist",
    goal="Draft Supreme Court of Ohio jurisdictional memoranda adhering strictly to S.Ct.Prac.R. formatting.",
    backstory="You are an appellate lawyer expert at framing propositions of law around fundamental due process and non-offending parent rights.",
    verbose=True,
)

# 2. Define Tasks
task_audit = Task(
    description="Analyze the case facts for unrecorded hearing codes like 'CR2 NR' and verify App.R. 9(C) compliance.",
    expected_output="Bullet list of structural errors found in the record.",
    agent=docket_auditor,
)

task_draft = Task(
    description="Draft a Memorandum in Support of Jurisdiction incorporating In re B.E. and ICPC arguments.",
    expected_output="Complete legal memorandum in markdown format.",
    agent=legal_writer,
)

# 3. Form the Crew
legal_crew = Crew(
    agents=[docket_auditor, legal_writer],
    tasks=[task_audit, task_draft],
    process=Process.sequential,
)

# 4. Run the Pipeline
if __name__ == "__main__":
    result = legal_crew.kickoff()
    print(result)
  
