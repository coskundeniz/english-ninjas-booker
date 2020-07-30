import json
from session_spec import SessionSpec


class Tutor:

    def __init__(self, name=None, tutor_id=None, session_spec=None):
        self.name = name
        self.tutor_id = tutor_id
        self.session_spec = session_spec

    def __str__(self):
    
        tutor_info = f"Tutor Name: {self.name}\nTutor id: {self.tutor_id}\n"
        tutor_info += "Preferred session properties\n"
        tutor_info += f"\tLength: {self.session_spec.get_session_length()}\n"
        tutor_info += f"\tHours preferred: {self.session_spec.get_preferred_hours()}\n"

        return tutor_info

    @classmethod
    def get_favourite_tutors(cls):
        """Read config file to get tutor and session specs

        Raises exception if there is an invalid field in config.

        :rtype: list
        :returns: List of Tutor objects
        """

        with open("tutors.json", "r") as tutors_file:
            tutors_config = json.load(tutors_file)

        if len(tutors_config["tutors"]) == 0:
            raise Exception("Please complete the config file.")

        favourite_tutors = []

        for item in tutors_config["tutors"]:

            session_length = item["preferred_session_length"]
            if session_length not in ["10", "20", "30", "60"]:
                raise Exception(f"Invalid session length({session_length}) for {item['name']}!")

            preferred_hours = item["preferred_hours_of_day"]
            if [hour for hour in preferred_hours if hour < 0 or hour > 23]:
                raise Exception(f"Invalid hour value for {item['name']}! Should be in range [0-23]")

            favourite_tutors.append(cls(item["name"], item["tutor_id"],
                                        SessionSpec(session_length,
                                                    preferred_hours)))

        return favourite_tutors


