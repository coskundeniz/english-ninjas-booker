import os
import sys
from time import sleep
from collections import namedtuple
from tutor import Tutor
from reporter import Reporter

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By 
    from selenium.webdriver.support.ui import WebDriverWait 
    from selenium.webdriver.support import expected_conditions as EC 
    from selenium.common.exceptions import TimeoutException
except ImportError:
    print("Please run 'pip install -r requirements.txt' or 'pipenv install'")
    sys.exit(1)


PAGE_ROOT = "https://englishninjas.com"
LOGIN_PAGE_URL = "https://englishninjas.com/signin?redirect=/student"


class Booker:
    """This class logins to page, and tries to book sessions
    according to config.

    Firefox is used as webdriver.

    For Linux systems, put geckodriver under /usr/bin or /usr/local/bin/
    For other platforms, see the following link

        https://selenium-python.readthedocs.io/installation.html
    """

    def __init__(self):
        self.timeout = 9
        self.browser = None

    def login_to_page(self, email=None, password=None):
        """Login to page with email and password

        If email and password were given as argument, these are used.
        Otherwise it looks for ENG_NINJAS_EMAIL, and ENG_NINJAS_PASSWD
        environment variables to get login information.

        :type email: str
        :param email: User email address for login
        :type password: str
        :param password: User password for login
        """

        try:
            self.browser = webdriver.Firefox()
        except:
            print("Make sure you have the geckodriver!")
            sys.exit(1)

        self.browser.get(LOGIN_PAGE_URL)

        try:
            # wait for form fields to load
            WebDriverWait(self.browser, self.timeout).until(EC.visibility_of_element_located((By.NAME, "email")))
        except TimeoutException:
            print("Timed out waiting for login page to load!")
            self.browser.quit() 

        email_field = self.browser.find_element_by_name("email")
        password_field = self.browser.find_element_by_name("password")

        email = email if email else os.environ["ENG_NINJAS_EMAIL"]
        password = password if password else os.environ["ENG_NINJAS_PASSWD"]
        email_field.send_keys(email)
        password_field.send_keys(password)

        submit_button = "/html/body/div[1]/div/div/div[2]/div[2]/div[4]/div/button"
        self.browser.find_element_by_xpath(submit_button).click()

    def book_session(self):
        """Book session from favourite tutors.
        Print the results if there are sessions booked.
        """

        booking_results = []
        BookingResult = namedtuple("BookingResult", "date message")

        try:
            favourite_tutor_list = Tutor.get_favourite_tutors()
        except Exception as e:
            print(e)
            self.browser.quit()
            sys.exit(1)

        for tutor in favourite_tutor_list:

            print(f"Booking a reservation from {tutor.name}...")

            self.browser.get(PAGE_ROOT + "/users/" + tutor.tutor_id)

            try:
                # wait for tutor avatar to be loaded
                tutor_avatar = "/html/body/div[2]/div[3]/span/img[1]"
                WebDriverWait(self.browser, self.timeout).until(
                    EC.visibility_of_element_located((By.XPATH, tutor_avatar))
                )
            except TimeoutException:
                print("Timed out waiting for tutor page to load! Continue with other tutors.")
                continue
            else:
                sleep(2)
                print("Clicking Book button...")

                try:
                    self.browser.find_element_by_css_selector(".n-booking-link").click()
                except:
                    print(f"No Book button found for {tutor.name}! Continue with other tutors.")
                    continue

            try:
                duration_button = "div.n-booking-modal-minutes > button:nth-child(1)"
                WebDriverWait(self.browser, self.timeout).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, duration_button))
                )
            except TimeoutException:
                print("Timed out waiting for duration/date buttons!")
                continue
            else:
                sleep(0.5)
                # click the duration button
                self.browser.find_element_by_css_selector(duration_button).click()

                session_length = tutor.session_spec.get_session_length()
                session_period_selector = f"div.n-booking-modal-minutes > div:nth-child(2) > ul:nth-child(2) > li:nth-child({(session_length // 10) + 1}) > a:nth-child(1)"
                print(f"Selecting {session_length} minutes for session duration...")

                sleep(1)

                self.browser.find_element_by_css_selector(session_period_selector).click()
                sleep(1)

                print("Selecting session date...")
                date_button = "div.n-booking-modal-dates > button:nth-child(1)"
                self.browser.find_element_by_css_selector(date_button).click()

                print("Getting all available sessions...")
                sleep(1)
                session_links = "div.n-booking-modal-dates > div:nth-child(2) > ul > li > a"
                all_sessions = self.browser.find_elements_by_css_selector(session_links)

                open_sessions = [sess for sess in all_sessions if "Booked" not in sess.text]
                suitable_time_slots = self._get_suitable_time_slots(open_sessions, tutor) 

                if not suitable_time_slots:
                    print(f"No available session found for {tutor.name}\n")
                    continue

                for session in suitable_time_slots:
                    session_date = session.text.split()[0]

                    if self._is_date_available(session_date, booking_results):
                        msg = f"Selected {session.text} session from {tutor.name}"
                        session.click()

                        sleep(1)

                        # confirm session booking
                        print("Confirming session booking...\n")
                        self.browser.find_element_by_css_selector(".n-btn-booking-modal-confirm").click()

                        sleep(1)

                        result = BookingResult(session_date, msg)
                        booking_results.append(result)

                        break

        if booking_results:
            reporter = Reporter()
            reporter.print_results(booking_results)
        else:
            print("Could not book a session!")

        self.browser.quit()

    def _get_suitable_time_slots(self, open_sessions, tutor):
        """Get suitable sessions of tutor according to config

        :type open_sessions: list
        :param open_sessions: All non-booked sessions of tutor
        :type tutor: Tutor
        :param tutor: Tutor object
        """

        suitable_time_slots = []
        preferred_hours = tutor.session_spec.get_preferred_hours()
    
        for session in open_sessions:
            for preferred_hour in preferred_hours:
                if session.text.split()[1].startswith(str(preferred_hour)):
                    suitable_time_slots.append(session)
        
        return suitable_time_slots

    def _is_date_available(self, date, booking_results):
        """Check if there is no session booked for given date

        :type date: str
        :param date: Session date 
        :type booking_results: list
        :param booking_results: Currently booked sessions
        :rtype: bool
        :returns: True if no sessions found for given date, False otherwise
        """

        for result in booking_results:
            if date == result.date:
                return False

        return True


