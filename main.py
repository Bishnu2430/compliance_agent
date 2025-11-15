from dotenv import load_dotenv
load_dotenv()  

from agents.orchestrator import Orchestrator
import os

def run_demo():
    orchestrator = Orchestrator()
    report = orchestrator.run_audit(
        documents_path="./sample_inputs/docs",
        repo_url=f"https://github.com/{os.getenv('GH_OWNER')}/{os.getenv('GH_REPO')}.git",
        create_pr=True,
        gh_owner=os.getenv("GH_OWNER"),
        gh_repo=os.getenv("GH_REPO")
    )
    print("Final report summary:")
    print(report)

if __name__ == "__main__":
    run_demo()
