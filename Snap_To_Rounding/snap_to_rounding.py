"""Snap selected Scribus elements to nearest specified increment along X or Y axis.

Author: Shin Tamaki
Version/Date: 1.0, 2024-09-30
Compatibility: Scribus v1.6.x, Fedora Workstation 40
"""

import sys

try:
    import scribus
except ImportError:
    print("This Python script is written for the Scribus scripting interface.")
    print("It can only be run from within Scribus.")
    sys.exit(1)


# FUNCTIONS
def get_unit_name():
    """Return the name of the unit based on the integer value."""
    unit_names = {
        0: "Points",
        1: "mm",
        2: "in",
        3: "picas",
        4: "cm",
        5: "cicero",
    }
    return unit_names.get(scribus.getUnit(), "Unknown unit")


def get_selected_objects():
    """Return a list of the names of all selected objects in the Scribus document."""
    return [scribus.getSelectedObject(i) for i in range(scribus.selectionCount())]


def get_user_input():
    """Prompt user for rounding increment and axis, with error handling.

    Returns:
        tuple: (rounding_increment (float), axis (str)) if valid.

    Raises:
        SystemExit: Exits the script if invalid input is provided.
    """
    # Prompt for axis, only accept 'X' or 'Y' (case-insensitive)
    try:
        axis = scribus.valueDialog(
            "Snap To Rounding (1/2)", "Alignment Axis (X or Y):", "X"
        ).upper()
        if axis not in {"X", "Y"}:
            scribus.messageBox(
                "Input Error",
                "Invalid axis. Please enter 'X' or 'Y'.",
                scribus.ICON_WARNING,
            )
            raise ValueError("Invalid input. Please enter 'X' or 'Y'.")
    except ValueError as e:
        print(e)
        sys.exit(1)

    # Prompt for rounding increment, allowing fractions
    document_unit = get_unit_name()
    rounding_increment_input = scribus.valueDialog(
        "Snap To Rounding (2/2)",
        f"Rounding Increment (e.g., 0.125 or 3/42){document_unit}:",
    )

    # Convert the rounding increment input to a float, allowing fractions
    try:
        # Evaluate fractions like "3/42" or convert directly to float
        rounding_increment = (
            eval(rounding_increment_input)
            if "/" in rounding_increment_input
            else float(rounding_increment_input)
        )
    except (ValueError, SyntaxError, ZeroDivisionError):
        scribus.messageBox(
            "Input Error",
            "Invalid rounding increment. Please enter a decimal or fraction.",
            scribus.ICON_WARNING,
        )
        sys.exit(1)

    return rounding_increment, axis


def round_to_increment(value, increment):
    """
    Rounds a given value to the nearest multiple of the specified increment.

    Parameters:
        value (float): Original position value.
        increment (float): Rounding increment.

    Returns:
        float: Rounded value.
    """
    return round(value / increment) * increment


def snap_position(element, rounding_increment, axis):
    """
    Adjusts the position of an element to the nearest specified increment along the specified axis.

    Parameters:
        element (str): The name of the selected element.
        rounding_increment (float): Increment for rounding.
        axis (str): Axis for snapping ('X' or 'Y').
    """
    x_pos, y_pos = scribus.getPosition(element)
    if axis == "X":
        x_pos = round_to_increment(x_pos, rounding_increment)
    else:
        y_pos = round_to_increment(y_pos, rounding_increment)

    scribus.moveObjectAbs(x_pos, y_pos, element)


def main(argv):
    """Main function to snap selected objects based on user input for rounding increment and axis."""
    if scribus.selectionCount() == 0:
        scribus.messageBox("Error", "No elements selected.", icon=scribus.ICON_NONE)
        return
    selection = get_selected_objects()
    rounding_increment, axis = get_user_input()
    for element in selection:
        snap_position(element, rounding_increment, axis)
    return


def main_wrapper(argv):
    """The main_wrapper() function disables redrawing, sets a sensible generic
    status bar message, and optionally sets up the progress bar. It then runs
    the main() function. Once everything finishes it cleans up after the main()
    function, making sure everything is sane before the script terminates."""
    try:
        scribus.statusMessage("Running script...")
        scribus.progressReset()
        main(argv)
    finally:
        # Exit neatly even if the script terminated with an exception,
        # so we leave the progress bar and status bar blank and make sure
        # drawing is enabled.
        if scribus.haveDoc():
            scribus.setRedraw(True)
        scribus.statusMessage("")
        scribus.progressReset()


# This code detects if the script is being run as a script, or imported as a module.
# It only runs main() if being run as a script. This permits you to import your script
# and control it manually for debugging.
if __name__ == "__main__":
    main_wrapper(sys.argv)
