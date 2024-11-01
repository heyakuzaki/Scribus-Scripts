"""Duplicate, Transform, Repeat for Fixed Count.

Automates the duplication and movement of objects a fixed number of times,
streamlining the process and maintaining a clean namespace.

Author: Shin Tamaki
Version/Date: 1.0, 2024-10-01
Compatibility: Scribus v1.6.x, Fedora Workstation 40
"""

import sys
import fractions

try:
    import scribus
except ImportError:
    print("This Python script is written for the Scribus scripting interface.")
    print("It can only be run from within Scribus.")
    sys.exit(1)


def get_unit_name():
    """Return the name of the unit based on the integer value."""
    unit_names = {
        0: "pt",
        1: "mm",
        2: "in",
        3: "picas",
        4: "cm",
        5: "cicero",
    }
    return unit_names.get(scribus.getUnit(), "Unknown unit")


# Function to prompt the user for the element name
def prompt_for_element_name(default_name):
    name_input = scribus.valueDialog(
        "Element Name",
        "Duplicates will have '_00X' suffix added.\nEnter the name of the element:",
        default_name,
    )
    if name_input == "":
        sys.exit(0)
    return name_input


# Function to prompt the user for the axis of duplication
def prompt_for_axis():
    while True:
        axis_input = scribus.valueDialog(
            "Axis for Duplication",
            "Enter 'X' for horizontal or 'Y' for vertical:",
            "X",
        )
        if axis_input == "":
            sys.exit(0)

        # Check if the user made a valid selection
        if axis_input.strip().upper() in ["X", "Y"]:
            return axis_input

        # If the selection is invalid, show an error message
        scribus.messageBox(
            "Error",
            "Invalid axis selected. Please enter 'X' or 'Y'.",
            icon=scribus.ICON_WARNING,
        )
    pass


# Function to prompt the user for the spacing between duplicates
def prompt_for_spacing():
    unit = get_unit_name()
    while True:
        # Prompt the user to enter the spacing, reminding them of the unit
        spacing_input = scribus.valueDialog(
            "Spacing",
            f"Document Unit({unit})\nEnter the spacing between duplicates e.g. 4, 2.34, or 4/32:",
        )
        if spacing_input == "":
            sys.exit(0)

        try:
            spacing_input = (
                float(fractions.Fraction(spacing_input))
                if "/" in spacing_input
                else float(spacing_input)
            )

            if spacing_input >= 0:
                return spacing_input

            # If the spacing is negative, show an error message
            scribus.messageBox(
                "Error", "Spacing must be 0 or greater.", icon=scribus.ICON_WARNING
            )

        except ValueError:
            scribus.messageBox(
                "Error",
                "Invalid input. Please enter a valid number (e.g., 4, 2.34, or 4/32).",
                icon=scribus.ICON_WARNING,
            )


# Function to prompt the user for the number of duplicates
def prompt_for_duplicate_count():
    while True:
        # Prompt the user to enter the number of duplicates
        count_input = scribus.valueDialog(
            "Number of Duplicates",
            "Enter the number of duplicates (whole number):",
            "1",
        )
        if count_input == "":
            sys.exit(0)

        try:
            if int(count_input) > 0:
                return int(count_input)

            # If the count is not positive, show an error message
            scribus.messageBox(
                "Error",
                "Number of duplicates must be greater than 0.",
                icon=scribus.ICON_WARNING,
            )

        except ValueError:
            scribus.messageBox(
                "Error",
                "Invalid input. Please enter a valid whole number.",
                icon=scribus.ICON_WARNING,
            )


def main(argv):
    """Main function"""
    if scribus.selectionCount() != 1:
        scribus.messageBox(
            "Error", "Please select exactly one element.", icon=scribus.ICON_NONE
        )
        return
    selected_element = scribus.getSelectedObject(0)
    element_name = prompt_for_element_name(selected_element)
    axis = prompt_for_axis()
    spacing = prompt_for_spacing()
    duplicate_count = prompt_for_duplicate_count()
    print(f"Original name: {selected_element}")
    print(f"Confirmed name: {element_name}")
    pass


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
