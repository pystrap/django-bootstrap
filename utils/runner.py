import subprocess


class Runner:
    @staticmethod
    def run(script, **kwargs):
        # Construct the command from the script and kwargs
        command = [script]
        for key, value in kwargs.items():
            command.extend(['--' + key, str(value)])

        # Execute the command
        result = subprocess.run(command, shell=True)

        # Check if the command was successful
        if result.returncode == 0:
            return True
        return False


# Example usage
# Runner.run("./create_website.sh", domain="test3.cweb.app", ip="203.161.61.79", username="node_manager")
