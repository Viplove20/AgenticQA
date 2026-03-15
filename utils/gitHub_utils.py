import subprocess
def push_to_github():

    answer = input("\nDo you want to push the changes to GitHub? (Y/N): ")

    if answer.lower() in ["y", "yes"]:

        print("📦 Committing and pushing code to GitHub...")

        subprocess.run(["git", "add", "."])
        subprocess.run(["git", "commit", "-m", "AI generated tests and execution results"])
        subprocess.run(["git", "push"])

        print("✅ Code pushed to GitHub")

    else:
        print("❌ Push cancelled")