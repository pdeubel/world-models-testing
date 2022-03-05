import logging
import subprocess
import tempfile
import time
from copy import deepcopy

import click
import numpy as np

from utils.setup_utils import initialize_logger


def evaluate_controller(controller_directory: str, gpu: int, stop_mode: str, amount: int, number_of_evaluations: int):
    python_commands = [
        "python", "evaluation/controller/_evaluation_run.py",
        f"--dir={controller_directory}",
        f"--gpu={gpu}"
    ]

    if stop_mode == "time":
        python_commands.append("-t")
    elif stop_mode == "iterations":
        python_commands.append("-i")
    else:
        raise RuntimeError(f"Stop mode '{stop_mode}' unknown")

    python_commands.append(f"--amount={amount}")

    xvfb_command = ["xvfb-run", "-a", "-s", "-screen 0 448x448x24"]

    temporary_files = [tempfile.NamedTemporaryFile(suffix=".npy") for _ in range(number_of_evaluations)]
    processes = []

    for i in range(number_of_evaluations):
        current_python_command = deepcopy(python_commands)
        current_python_command.append(f"--tmp-file={temporary_files[i].name}")

        command = xvfb_command + current_python_command

        # Sleep a bit before starting a new process, to avoid getting a duplicate server number
        time.sleep(0.25)
        p = subprocess.Popen(command)
        processes.append(p)

        logging.info(f"Started process with command {command}")

    for i, p in enumerate(processes):
        p.wait()
        logging.info(f"Finished process {i}")

    logging.info("Finished all processes, gathering evaluation")

    rewards = []

    for tmp_file in temporary_files:
        rewards.append(np.load(tmp_file.name).item())

    logging.info(f"Controller Evaluation")
    logging.info(f"Max {np.max(rewards):.6f} - Mean {np.mean(rewards):.6f} - Std {np.std(rewards):.6f} - "
                 f"Min {np.min(rewards):.6f}")
    logging.info("Finished")

    return rewards


def evaluation_options(function):
    function = click.option("-c", "--dir", "controller_directory", type=str, required=True,
                            help="Path to a trained controller")(function)
    function = click.option("-g", "--gpu", type=int, default=-1,
                            help="GPU on which evaluation shall run, -1 means cpu")(function)
    function = click.option("-t", "--time", "stop_mode", flag_value="time",
                            help="Use elapsed time in seconds to evaluate")(function)
    function = click.option("-i", "--iterations", "stop_mode", default=True, flag_value="iterations",
                            help="Use the number of iterations to evaluate")(function)
    function = click.option("--amount", type=int, help="Amount on how long the evaluation shall run (seconds or "
                                                       "number of iterations, depending on the stop_mode")(function)
    return function


@click.command()
@evaluation_options
@click.option("-n", "--number-of-evaluations", type=int, default=1, help="Number of evaluations")
def main(controller_directory: str, gpu: int, stop_mode: str, amount: int, number_of_evaluations: int):
    """
    Evaluate a trained controller on the actual environment for number_of_evaluations

    To be used more inside another script, for example in train_controller as there the output is actually logged
    to TensorBoard (and Comet). Here only an output is printed.

    """
    logger, _ = initialize_logger()
    logger.setLevel(logging.INFO)

    evaluate_controller(
        controller_directory=controller_directory,
        gpu=gpu,
        stop_mode=stop_mode,
        amount=amount,
        number_of_evaluations=number_of_evaluations
    )


if __name__ == "__main__":
    main()
