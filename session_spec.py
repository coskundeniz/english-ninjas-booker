
class SessionSpec:

    def __init__(self, session_length, preferred_hours_of_day):
        self.session_length = int(session_length)
        self.preferred_hours = preferred_hours_of_day

    def get_session_length(self):
        """Get session length
            
        :rtype: int
        :returns: Session length in minutes
        """

        return self.session_length

    def get_preferred_hours(self):
        """Get preferred hours for session booking

        :rtype: list
        :returns: Preferred hours of the day for session 
        """

        for i, hour in enumerate(self.preferred_hours):
            if hour < 10:
                self.preferred_hours[i] = "0"+str(hour)

        return self.preferred_hours


