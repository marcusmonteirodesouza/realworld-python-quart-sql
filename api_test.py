import os.path
import shutil
import subprocess
import sys
import validators

if __name__ == "__main__":
    if not shutil.which("git"):
        sys.exit("'git' command not found. Please install 'git' before proceeding.")

    if not shutil.which("npm"):
        sys.exit("'npm' command not found. Please install 'Node.js' before proceeding.")

    subprocess.run("npm install --global newman", shell=True, check=True)

    APIURL = os.getenv("APIURL")
    if not APIURL:
        APIURL = input("Please input the APIURL: ")

    if not validators.url(APIURL):
        raise ValueError(f"APIURL must be a valid url. Received {APIURL}")

    this_script_dir = os.path.dirname(os.path.realpath(sys.argv[0]))

    run_api_tests_executable_path = os.path.join(
        this_script_dir, "realworld", "api", "run-api-tests.sh"
    )

    if not os.path.isfile(run_api_tests_executable_path):
        subprocess.run(
            ["git", "submodule", "update", "--init", "--recursive"],
            check=True,
            cwd=this_script_dir,
        )

    subprocess.run(
        f"APIURL={APIURL} {run_api_tests_executable_path}", shell=True, check=True
    )
