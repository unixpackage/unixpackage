from subprocess import check_output, call
from os import path, chdir
import hitchpython
import hitchtest
import hitchcli


# Get directory above this file
PROJECT_DIRECTORY = path.abspath(path.join(path.dirname(__file__), '..'))

class ExecutionEngine(hitchtest.ExecutionEngine):
    """Engine for orchestating and interacting with the app."""

    def set_up(self):
        """Ensure virtualenv present, then run all services."""
        self.cli_steps = hitchcli.CommandLineStepLibrary(default_timeout=240)

        self.cd = self.cli_steps.cd
        self.run = self.cli_steps.run
        self.expect = self.cli_steps.expect
        self.send_control = self.cli_steps.send_control
        self.send_line = self.cli_steps.send_line
        self.send_signal = self.cli_steps.send_signal
        self.exit_with_any_code = self.cli_steps.exit_with_any_code
        self.show_output = self.cli_steps.show_output
        self.exit = self.cli_steps.exit

        if self.preconditions is not None and "python_version" in self.preconditions:
            self.python_package = hitchpython.PythonPackage(
                python_version=self.preconditions['python_version']
            )
            self.python_package.build()
            self.python_package.verify()

        if self.preconditions is not None and "vagrant" in self.preconditions:
            self.cd(self.preconditions["vagrant"])
            self.run("vagrant up")
            self.exit_with_any_code()

    def pause(self, message=None):
        """Stop. IPython time."""
        self.ipython(message)

    def install_in_virtualenv(self):
        chdir(PROJECT_DIRECTORY)
        call([self.python_package.pip, "uninstall", "unixpackage", "-y"])
        check_output([self.python_package.pip, "install", "."])

    def unixpackage(self, arguments):
        self.run("{} {}".format(
            path.join(self.python_package.bin_directory, "unixpackage"),
            arguments,
        ))

    def vagrant_ssh(self, command):
        self.run("vagrant", args=["ssh", "-c", command])

    def on_failure(self):
        """Stop and IPython."""
        if not self.settings['quiet']:
            if self.settings.get("pause_on_failure", True):
                self.pause(message=self.stacktrace.to_template())

    def on_success(self):
        """Ka-ching!"""
        if self.settings.get("pause_on_success", False):
            self.pause(message="SUCCESS")

    def tear_down(self):
        if self.preconditions is not None and "vagrant" in self.preconditions:
            self.run("vagrant halt")
            self.exit_with_any_code()
