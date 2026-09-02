import os
from crewai import Agent, Crew, Process, Task, LLM

GEMINI_KEY = "AQ.Ab8RN6LJt9_ihNoSz88iPZyaDoJC_vxey7oLYE8DKNPzehuQ8g"
os.environ["GEMINI_API_KEY"] = GEMINI_KEY

gemini_llm = LLM(
    model="gemini/gemini-1.5-flash",
    api_key=GEMINI_KEY
)

docket_auditor = Agent(
    role="Procedural & Docket Auditor",
    goal="Identify unrecorded hearings, missing transcripts, and statutory violations in juvenile court dockets.",
    backstory="You are a meticulous paralegal specializing in auditing trial court dockets for structural errors under Juv.R. 37(A) and App.R. 9(C).",
    verbose=True,
    llm=gemini_llm,
)

legal_writer = Agent(
    role="Appellate Brief Specialist",
    goal="Draft Supreme Court of Ohio jurisdictional memoranda adhering strictly to S.Ct.Prac.R. formatting.",
    backstory="You are an appellate lawyer expert at framing propositions of law around fundamental due process and non-offending parent rights.",
    verbose=True,
    llm=gemini_llm,
)

task_audit = Task(
    description="Analyze the case facts for unrecorded hearing codes like 'CR2 NR' and verify App.R. 9(C) compliance.",
    expected_output="Bullet list of structural errors found in the record.",
    agent=docket_auditor,
)

task_draft = Task(
    description="Draft a Memorandum in Support of Jurisdiction incorporating In re B.E. and ICPC arguments.",
    expected_output="Complete legal memorandum in markdown format.",
    agent=legal_writer,
    output_file="appellate_brief.md"
)

legal_crew = Crew(
    agents=[docket_auditor, legal_writer],
    tasks=[task_audit, task_draft],
    process=Process.sequential,
)

if __name__ == "__main__":
    result = legal_crew.kickoff()
    print(result)
    
