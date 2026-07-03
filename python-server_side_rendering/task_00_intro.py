#!/usr/bin/python3
"""Generate personalized invitation files from a template."""
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_invitations(template, attendees):
    """Generate output_X.txt invitation files from a template and attendees."""
    if not isinstance(template, str):
        logger.error("Template must be a string.")
        return
    if not isinstance(attendees, list) or not all(
        isinstance(attendee, dict) for attendee in attendees
    ):
        logger.error("Attendees must be a list of dictionaries.")
        return

    if not template:
        logger.error("Template is empty, no output files generated.")
        return
    if not attendees:
        logger.error("No data provided, no output files generated.")
        return

    for index, attendee in enumerate(attendees, start=1):
        content = template
        for key in ("name", "event_title", "event_date", "event_location"):
            value = attendee.get(key)
            if value is None:
                value = "N/A"
            content = content.replace("{" + key + "}", str(value))

        filename = "output_{}.txt".format(index)
        with open(filename, "w") as output_file:
            output_file.write(content)
